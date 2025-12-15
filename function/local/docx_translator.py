import io
from collections import defaultdict
from docx import Document
from docx.text.paragraph import Paragraph
from docx.text.run import Run
from concurrent.futures import ThreadPoolExecutor, as_completed
import operator
import re


from function.AzureAIClient import AzureAiClient
from app_config.keys_config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_TOKEN, XINFERENCE_TRANSLATE_MODEL_NAME
from function.local.XinferenceChatClient import XinferenceChatClient

# =================================================================
#  调用 Xinference 的翻译函数
# =================================================================
def get_llm_translation_xinference(text_to_translate: str, context: str, target_language: str) -> str:
    """调用通过 Xinference 部署的大模型进行翻译。"""
    try:
        # 初始化 Xinference 客户端
        xin_client = XinferenceChatClient()
        # print(f"--- [Xinference] 正在翻译 (原文): {text_to_translate}")
        
        # 默认的错误返回信息
        translated_text = f"*******[Xinference] 翻译失败: {text_to_translate}*******"

        # 构建与 Azure 版本完全一致的 messages
        messages = [
            {"role": "system", "content": f"你是一个专业的翻译助手。请将用户提供的文本翻译成{target_language}。请注意保持翻译的专业性和准确性，并参考上下文, 不要丢失标点符号以及空格。"},
            {"role": "user", "content": f"为了帮助你理解，这是该文本所在的完整段落上下文：\n---\n{context}\n---"},
            {"role": "user", "content": f"请仅翻译以下内容，不要添加任何额外的解释或标签：\n---\n{text_to_translate}\n---"}
        ]

        # 调用 Xinference 模型
        non_stream_response = xin_client.chat(
            messages=messages,
            model=XINFERENCE_TRANSLATE_MODEL_NAME,
            stream=False,
        )
        if non_stream_response and non_stream_response.choices:
            translated_text = non_stream_response.choices[0].message.content.strip()
            cleaned_response = re.sub(r"<think>.*?</think>\n\n", "", translated_text, flags=re.DOTALL).strip()

            # print(f"--- [Xinference] 正在翻译 (原文): {text_to_translate}")
            # print(f"--- [Xinference] 上下文: {context}")
            # print(f"--- [Xinference] 正在翻译 (翻译结果): {translated_text}")
            # print(f"--- [Xinference] 正在翻译 (处理后): {cleaned_response}")

            return cleaned_response

    except Exception as e:
        print(f"!!!调用 Xinference 时出错: {e}")
        return translated_text # 返回带有错误标记的原文
    
    return translated_text

def get_llm_translation(text_to_translate: str, context: str, target_language: str) -> str:
    """调用大模型进行翻译 (此为您的原始 Azure 版本)"""
    az_AiClient = AzureAiClient(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_TOKEN
    )
    print(f"--- [Azure] 正在翻译 (原文): {text_to_translate}")
    translated_text = f"*******[Azure] 翻译失败: {text_to_translate}*******"
    messages = [
        {"role": "system", "content": f"你是一个专业的翻译助手。请将用户提供的文本翻译成{target_language}。请注意保持翻译的专业性和准确性，并参考上下文, 不要丢失标点符号。"},
        {"role": "user", "content": f"为了帮助你理解，这是该文本所在的完整段落上下文：\n---\n{context}\n---"},
        {"role": "user", "content": f"请仅翻译以下内容，不要添加任何额外的解释或标签：\n---\n{text_to_translate}\n---"}
    ]
    try:
        non_stream_response = az_AiClient.get_chat_completion(
            messages=messages,
            model="gpt-4.1-mini",
            stream=False,
        )
        if non_stream_response and non_stream_response.choices:
            return non_stream_response.choices[0].message.content.strip()
    except Exception as e:
        print(f"!!! 调用Azure AI时出错: {e}")
        return translated_text
    return translated_text

def get_run_style(run: Run):
    """获取Run的样式 (此函数无需修改)"""
    font = run.font
    return (font.name, font.size, font.bold, font.italic, font.underline, font.color.rgb if font.color and font.color.rgb else None, font.highlight_color)

def apply_style_to_run(source_run: Run, target_run: Run):
    """将源Run的样式应用到目标Run (此函数无需修改)"""
    target_run.font.name = source_run.font.name
    target_run.font.size = source_run.font.size
    target_run.font.bold = source_run.font.bold
    target_run.font.italic = source_run.font.italic
    target_run.font.underline = source_run.font.underline
    if source_run.font.color and source_run.font.color.rgb:
        target_run.font.color.rgb = source_run.font.color.rgb
    if source_run.font.highlight_color:
        target_run.font.highlight_color = source_run.font.highlight_color

def translate_docx_in_memory(
    input_file_obj, 
    target_language: str = "English", 
    progress_callback=None
):
    """
    主函数：使用多线程并发翻译DOCX文件流。
    采用“收集-执行-重建”模式，并已修正顺序问题。
    """
    doc = Document(input_file_obj)
    
    # --- 阶段 1: 收集所有需要翻译的任务 (并记录顺序) ---
    tasks = []
    all_paragraphs = list(doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                all_paragraphs.extend(cell.paragraphs)

    print(f"发现 {len(all_paragraphs)} 个段落。正在分析并拆分文本块...")

    for para in all_paragraphs:
        paragraph_context = para.text
        if not para.runs or not paragraph_context.strip():
            continue
        
        chunk_index_in_para = 0
        current_text_chunk = ""
        # 确保段落有内容再访问第一个run
        if not para.runs: continue
        style_of_chunk = para.runs[0]

        for run in para.runs:
            if get_run_style(run) == get_run_style(style_of_chunk):
                current_text_chunk += run.text
            else:
                if current_text_chunk.strip():
                    tasks.append({
                        'text': current_text_chunk,
                        'style_run': style_of_chunk,
                        'parent_para': para,
                        'context': paragraph_context,
                        'chunk_index': chunk_index_in_para
                    })
                    chunk_index_in_para += 1
                current_text_chunk = run.text
                style_of_chunk = run
        
        if current_text_chunk.strip():
            tasks.append({
                'text': current_text_chunk,
                'style_run': style_of_chunk,
                'parent_para': para,
                'context': paragraph_context,
                'chunk_index': chunk_index_in_para
            })
            
    total_tasks = len(tasks)
    if total_tasks == 0:
        print("未发现需要翻译的文本内容。")
        # 如果没有内容，直接返回原始文件流
        input_file_obj.seek(0)
        return input_file_obj

    print(f"共找到 {total_tasks} 个独立的文本块需要翻译。开始并发翻译...")

    # --- 阶段 2: 并发执行翻译任务 ---
    reconstruction_data = defaultdict(list)
    processed_count = 0
    
    MAX_WORKERS = 10
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # 【请在此处选择要使用的翻译函数】
        # 将 get_llm_translation 替换为 get_llm_translation_xinference 即可切换
        # 
        # 使用 Azure (原始版本):
        # target_translation_function = get_llm_translation
        #
        # 使用 Xinference (新版本):
        target_translation_function = get_llm_translation_xinference

        future_to_task = {
            executor.submit(target_translation_function, task['text'], task['context'], target_language): task
            for task in tasks
        }

        for future in as_completed(future_to_task):
            task = future_to_task[future]
            parent_para = task['parent_para']
            
            try:
                translated_text = future.result()
                reconstruction_data[parent_para].append({
                    'text': translated_text,
                    'style_run': task['style_run'],
                    'chunk_index': task['chunk_index'] 
                })
            except Exception as exc:
                print(f"!!! 文本块 '{task['text'][:30]}...' 翻译生成了一个异常: {exc}")
                reconstruction_data[parent_para].append({
                    'text': task['text'], # 翻译失败，保留原文
                    'style_run': task['style_run'],
                    'chunk_index': task['chunk_index']
                })
            
            processed_count += 1
            if progress_callback:
                progress_callback(processed_count / total_tasks)

    # --- 阶段 3: 在主线程中安全地重建文档 (并排序) ---
    print("所有翻译任务已完成。正在重建文档...")
    
    for para, translated_chunks in reconstruction_data.items():
        sorted_chunks = sorted(translated_chunks, key=operator.itemgetter('chunk_index'))

        # 清空段落现有内容
        p = para._p
        p.clear_content()

        # 根据排序后的chunks重建段落
        for chunk in sorted_chunks:
            new_run = para.add_run(chunk['text'])
            apply_style_to_run(chunk['style_run'], new_run)

    print("文档重建完成。")
    
    output_buffer = io.BytesIO()
    doc.save(output_buffer)
    output_buffer.seek(0)
    
    return output_buffer
