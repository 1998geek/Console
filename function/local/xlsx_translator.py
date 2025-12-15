# 文件名: xlsx_translator.py

import io
import re
import openpyxl
from concurrent.futures import ThreadPoolExecutor, as_completed

# =================================================================
#  请确保这些自定义模块在您的项目路径中
# =================================================================
from function.AzureAIClient import AzureAiClient
from app_config.keys_config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_TOKEN, XINFERENCE_TRANSLATE_MODEL_NAME
from function.local.XinferenceChatClient import XinferenceChatClient

# =================================================================
# 1. 翻译函数 (保持不变)
# =================================================================

def get_llm_translation_xinference(text_to_translate: str, target_language: str) -> str:
    """调用通过 Xinference 部署的大模型进行翻译。"""
    try:
        xin_client = XinferenceChatClient()
        translated_text = f"*******[Xinference] 翻译失败: {text_to_translate}*******"
        messages = [
            {"role": "system", "content": f"你是一个专业的翻译助手。请将以下文本翻译成{target_language}。请仅返回翻译后的文本，不要添加任何额外的解释、标签或上下文说明。"},
            {"role": "user", "content": text_to_translate}
        ]
        non_stream_response = xin_client.chat(
            messages=messages, model=XINFERENCE_TRANSLATE_MODEL_NAME, stream=False,
        )
        if non_stream_response and non_stream_response.choices:
            translated_text = non_stream_response.choices[0].message.content.strip()
            cleaned_response = re.sub(r"<think>.*?</think>\n\n", "", translated_text, flags=re.DOTALL).strip()
            return cleaned_response
    except Exception as e:
        print(f"!!! 调用 Xinference 时出错: {e}")
        return translated_text
    return translated_text

def get_llm_translation(text_to_translate: str, target_language: str) -> str:
    """调用大模型进行翻译 (Azure 版本)"""
    az_AiClient = AzureAiClient(azure_endpoint=AZURE_OPENAI_ENDPOINT, api_key=AZURE_OPENAI_TOKEN)
    print(f"--- [Azure] 正在翻译 (原文): {text_to_translate}")
    translated_text = f"*******[Azure] 翻译失败: {text_to_translate}*******"
    messages = [
        {"role": "system", "content": f"你是一个专业的翻译助手，负责将文本翻译成{target_language}。请仅返回翻译后的文本，不要添加任何额外的解释或标签。"},
        {"role": "user", "content": text_to_translate}
    ]
    try:
        non_stream_response = az_AiClient.get_chat_completion(
            messages=messages, model="gpt-4.1-mini", stream=False,
        )
        if non_stream_response and non_stream_response.choices:
            return non_stream_response.choices[0].message.content.strip()
    except Exception as e:
        print(f"!!! 调用Azure AI时出错: {e}")
        return translated_text
    return translated_text

# =================================================================
# 2. 主封装函数 (已增加 translate_sheet_names 参数)
# =================================================================
def translate_xlsx_in_memory(
    input_file_obj, 
    target_language: str = "English", 
    translate_sheet_names: bool = False, # <--- 新增的控制参数
    progress_callback=None
):
    """
    主函数：使用多线程并发翻译Excel文件流。
    
    参数:
        input_file_obj: 输入的Excel文件流。
        target_language: 目标翻译语言。
        translate_sheet_names (bool): 是否翻译工作表的名称。默认为False。
                                      警告：设置为True可能会破坏工作表之间的公式链接。
        progress_callback: 进度回调函数。
    """
    workbook = openpyxl.load_workbook(input_file_obj)
    
    # --- 阶段 1: 收集所有需要翻译的任务 ---
    tasks = []
    
    # 1a. 收集所有需要翻译的单元格 (始终执行)
    for sheet in workbook.worksheets:
        for row in sheet.iter_rows():
            for cell in row:
                if cell.data_type == 's' and cell.value and cell.value.strip():
                    tasks.append({
                        'type': 'cell',
                        'text': cell.value,
                        'target_object': cell
                    })
                    
    # 1b. 【条件执行】根据参数决定是否收集工作表名称
    if translate_sheet_names:
        print("\n[警告] 已启用工作表名称翻译。这可能会破坏文件中的公式链接！\n")
        for sheet in workbook.worksheets:
            if sheet.title and sheet.title.strip():
                tasks.append({
                    'type': 'sheet',
                    'text': sheet.title,
                    'target_object': sheet
                })

    total_tasks = len(tasks)
    if total_tasks == 0:
        print("未发现需要翻译的文本项。")
        input_file_obj.seek(0)
        return input_file_obj

    print(f"发现 {total_tasks} 个需要翻译的文本项。开始并发翻译...")

    # --- 阶段 2 & 3: 并发执行并写回结果 ---
    processed_count = 0
    MAX_WORKERS = 10 

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 【请在此处选择要使用的翻译函数】
        # target_translation_function = get_llm_translation
        target_translation_function = get_llm_translation_xinference

        future_to_task = {
            executor.submit(target_translation_function, task['text'], target_language): task
            for task in tasks
        }

        for future in as_completed(future_to_task):
            task = future_to_task[future]
            try:
                translated_text = future.result()
                
                if task['type'] == 'cell':
                    task['target_object'].value = translated_text
                elif task['type'] == 'sheet':
                    task['target_object'].title = translated_text
                    
            except Exception as exc:
                print(f"!!! 任务 '{task['text'][:30]}...' (类型: {task['type']}) 翻译时出现异常: {exc}")
            
            processed_count += 1
            if progress_callback:
                progress_callback(processed_count / total_tasks)
    
    print("所有翻译任务已完成。")
    
    output_buffer = io.BytesIO()
    workbook.save(output_buffer)
    output_buffer.seek(0)
    
    return output_buffer