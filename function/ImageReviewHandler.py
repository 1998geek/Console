import base64
import json
import io
import concurrent.futures
from datetime import date
from openai import AzureOpenAI
from app_config.keys_config import AZURE_OPENAI_TOKEN, AZURE_OPENAI_ENDPOINT
from app_config.prompt_config import load_prompt
from app_config.settings import get_setting

# --- Constants ---
# IMAGE_BATCH_THRESHOLD = 10  # 小于等于此数量的图片将被打包一次性发送
IMAGE_BATCH_THRESHOLD = get_setting("IMAGE_BATCH_THRESHOLD")

# --- AI Client Initialization ---
def get_ai_client():
    """
    Initializes and returns an instance of the AzureOpenAI client.
    """
    if not all([AZURE_OPENAI_TOKEN, AZURE_OPENAI_ENDPOINT]) or \
       "YOUR_AZURE" in AZURE_OPENAI_TOKEN:
        raise ValueError("请在 `app_config/keys_config.py` 文件中配置您的 Azure OpenAI 凭据。" )
    
    try:
        client = AzureOpenAI(
            api_key=AZURE_OPENAI_TOKEN,
            api_version="2025-01-01-preview",  # Using a stable, recommended API version
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        return client
    except Exception as e:
        raise RuntimeError(f"初始化 Azure AI Client 时发生错误: {e}") from e

# --- Image Conversion Utility ---
def image_bytes_to_base64(image_data):
    """
    Converts image data into a Base64 encoded data URL.
    """
    if isinstance(image_data, tuple) and len(image_data) == 2:
        image_bytes, content_type = image_data
    else:
        try:
            buffer = io.BytesIO()
            image_format = image_data.format or 'PNG'
            image_data.save(buffer, format=image_format)
            image_bytes = buffer.getvalue()
            content_type = f"image/{image_format.lower()}"
        except AttributeError:
            raise TypeError(f"Unsupported data type for image conversion: {type(image_data)}")

    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:{content_type};base64,{base64_image}"

# --- Internal Helper for Reviewing a SET of Images ---
def _review_images_as_set(ai_client, content, images):
    """
    Performs a multimodal check for a BATCH of images in a single call.
    """
    current_date_str = f"请注意：为方便你判断有效期等信息，当前系统日期是 {date.today().isoformat()}."
    enhanced_content = f"{current_date_str}\n\n---\n\n{content}"
    
    user_message_content = [{"type": "text", "text": enhanced_content}]
    for img_data in images:
        try:
            base64_url = image_bytes_to_base64(img_data)
            user_message_content.append({
                "type": "image_url",
                "image_url": {"url": base64_url}
            })
        except (TypeError, AttributeError) as e:
            return [{"status": "error", "summary": f"❌ 批量图片转换失败: {e}"}] * len(images)

    system_prompt = load_prompt(is_batch=True)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message_content},
        {"role": "user", "content": "当前图片数量是 " + str(len(images)) + " 张。"},
        {"role": "user", "content": "请注意：你必须返回一个JSON数组，数组中的每一个JSON对象都代表一张图片的审查结果，并且必须与输入图片的数量顺序完全一致"}
    ]

    try:
        response = ai_client.chat.completions.create(
            model="gpt-5-chat", 
            messages=messages,
            max_tokens=1500,
            temperature=0.1,
        )
        response_content = response.choices[0].message.content
        json_string = response_content.strip().replace("```json", "").replace("```", "")
        results = json.loads(json_string)
        
        if len(results) != len(images):
            no = "❌ AI返回的结果数量与请求的图片数量不匹配。"

        if isinstance(results, list) and all("status" in r and "summary" in r for r in results):
            return results
        else:
            return [{"status": "error", "summary": f"❌ AI返回了无效的JSON列表格式。收到内容: {response_content}"}] * len(images)

    except json.JSONDecodeError:
        return [{"status": "error", "summary": f"❌ AI返回的格式无法解析为JSON。收到的内容: {response_content}"}] * len(images)
    except Exception as e:
        return [{"status": "error", "summary": f"❌ 调用AI模型时发生API错误: {str(e)}"}] * len(images)

# --- Internal Helper for Reviewing a SINGLE Image ---
def _review_image_individually(ai_client, content, image_data):
    """
    Performs a multimodal check for a SINGLE image.
    """
    current_date_str = f"请注意：为方便你判断有效期等信息，当前系统日期是 {date.today().isoformat()}."
    enhanced_content = f"{current_date_str}\n\n---\n\n{content}"
    user_message_content = [{"type": "text", "text": enhanced_content}]
    
    try:
        base64_url = image_bytes_to_base64(image_data)
        user_message_content.append({
            "type": "image_url",
            "image_url": {"url": base64_url}
        })
    except (TypeError, AttributeError) as e:
        return {"status": "error", "summary": f"❌ 图片格式无效或转换失败: {e}"}
    
    system_prompt = load_prompt()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message_content}
    ]

    try:
        response = ai_client.chat.completions.create(
            model="gpt-5-chat", 
            messages=messages,
            max_tokens=1500,
            temperature=0.1,
        )
        response_content = response.choices[0].message.content
        json_string = response_content.strip().replace("```json", "").replace("```", "")
        result = json.loads(json_string)
        
        if isinstance(result, dict) and "status" in result and "summary" in result:
            return result
        else:
            return {"status": "error", "summary": f"❌ AI返回了无效的JSON格式。收到内容: {response_content}"}

    except json.JSONDecodeError:
        return {"status": "error", "summary": f"❌ AI返回的格式无法解析为JSON。收到的内容: {response_content}"}
    except Exception as e:
        return {"status": "error", "summary": f"❌ 调用AI模型时发生API错误: {str(e)}"}

# --- Main LLM Check Function (Re-architected to fix indexing bug) ---
def perform_llm_check(ai_client, content, images):
    """
    Reviews a list of images, preserving order and handling placeholders correctly.
    """
    if not ai_client:
        return [{"status": "error", "summary": "❌ AI客户端未正确初始化。"}] * len(images)

    if not images:
        return [{"status": "info", "summary": "ℹ️ 本章节无任何图片内容。"}]

    # Step 1: Initialize final results list and identify valid/invalid images
    final_results = [None] * len(images)
    valid_images_to_process = []
    
    for i, img_data in enumerate(images):
        if isinstance(img_data, str):
            # Immediately create a placeholder result for invalid image formats
            summary = f"ℹ️ 跳过不支持的图片格式或加载失败的图片 (原始占位符: {img_data})"
            final_results[i] = {"status": "info", "summary": summary}
        else:
            # Collect valid images along with their original index
            valid_images_to_process.append((i, img_data))

    # If no valid images, we can return the list of placeholders
    if not valid_images_to_process:
        print("INFO: No valid images to process for AI review.")
        return final_results

    # Step 2: Process the valid images using the appropriate strategy
    num_valid_images = len(valid_images_to_process)
    original_indices = [item[0] for item in valid_images_to_process]
    image_objects = [item[1] for item in valid_images_to_process]

    ai_results = []
    # Strategy 1: Batch processing
    if 0 < num_valid_images <= IMAGE_BATCH_THRESHOLD:
        print(f"INFO: Processing {num_valid_images} valid images as a single batch.")
        ai_results = _review_images_as_set(ai_client, content, image_objects)
    # Strategy 2: Concurrent individual processing
    else:
        print(f"INFO: Processing {num_valid_images} valid images concurrently.")
        def worker(image_data):
            return _review_image_individually(ai_client, content, image_data)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            ai_results = list(executor.map(worker, image_objects))

    # Step 3: Populate the final results list using original indices
    if len(ai_results) == len(original_indices):
        for i, ai_res in enumerate(ai_results):
            original_idx = original_indices[i]
            final_results[original_idx] = ai_res
    else:
        # If AI returns a malformed list, create error placeholders
        error_summary = f"❌ AI返回的结果数量 ({len(ai_results)}) 与请求的图片数量 ({len(original_indices)}) 不匹配。"
        for original_idx in original_indices:
            final_results[original_idx] = {"status": "error", "summary": error_summary}

    print("INFO: All image processing tasks completed.")
    return final_results