import io
import logging
import asyncio
from functools import partial
from typing import Optional, Union
from app.services.azure_ai import AzureLLMService
from app.services.azure_translator import AzureDocumentTranslator
from app.services.tasks.task_manager import TaskManager
from app.utils.doc_parsers import DocxParser, XlsxParser, PptxParser

logger = logging.getLogger(__name__)

class TranslationService:
    """
    Service for translating documents using LLMs or Cloud Translation.
    Integrates with doc_parsers for file handling and AzureLLMService for AI capabilities.
    """
    def __init__(self):
        self.llm_service = AzureLLMService()
        self.cloud_translator = AzureDocumentTranslator()
        self.docx_parser = DocxParser()
        self.xlsx_parser = XlsxParser()
        self.pptx_parser = PptxParser()

    async def translate_by_cloud(self, file_content: bytes, filename: str, target_language: str) -> io.BytesIO:
        """
        Translate document using Azure Document Translation (Cloud).
        """
        logger.info(f"Starting Cloud translation for {filename} to {target_language}")
        
        loop = asyncio.get_running_loop()

        # 1. Upload to source container
        await loop.run_in_executor(
            None,
            partial(
                self.cloud_translator.storage.upload_blob,
                self.cloud_translator.source_container,
                filename,
                file_content
            )
        )

        # 2. Start translation (blocking wait)
        await loop.run_in_executor(
            None,
            partial(
                self.cloud_translator.start_translation,
                filename,
                target_language
            )
        )

        # 3. Download from target container
        translated_content = await loop.run_in_executor(
            None,
            partial(
                self.cloud_translator.storage.download_blob,
                self.cloud_translator.target_container,
                filename
            )
        )
        
        return io.BytesIO(translated_content)

    async def start_cloud_translation_task(self, file_content: bytes, filename: str, target_language: str) -> str:
        """
        Start an asynchronous cloud translation task.
        Returns the task_id.
        """
        # 1. Init Task
        task_id = TaskManager.init_task("cloud_translation", metadata={"filename": filename, "target_lang": target_language})
        
        # 2. Run in background
        # We use asyncio.create_task to run the polling loop in background without blocking the API response
        asyncio.create_task(self._run_cloud_translation(task_id, file_content, filename, target_language))
        
        return task_id

    async def _run_cloud_translation(self, task_id: str, file_content: bytes, filename: str, target_language: str):
        try:
            # 1. Upload
            TaskManager.update_progress(task_id, 10, "Uploading file...")
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                partial(
                    self.cloud_translator.storage.upload_blob,
                    self.cloud_translator.source_container,
                    filename,
                    file_content
                )
            )
            
            # Check if target exists
            exists = await loop.run_in_executor(
                None,
                partial(self.cloud_translator.check_target_exists, filename)
            )
            
            if exists:
                TaskManager.update_progress(task_id, 90, "Target file already exists. Generating download link...")
                result_url = self.cloud_translator.storage.generate_blob_sas_url(
                    container_name=self.cloud_translator.target_container,
                    blob_name=filename
                )
                TaskManager.complete_task(task_id, {"download_url": result_url})
                return

            # 2. Start Async Translation
            TaskManager.update_progress(task_id, 30, "Submitting translation job...")
            operation_id = await loop.run_in_executor(
                None,
                partial(
                    self.cloud_translator.start_translation_async,
                    filename,
                    target_language
                )
            )
            
            # 3. Poll
            while True:
                status = await loop.run_in_executor(
                    None,
                    partial(
                        self.cloud_translator.check_translation_status,
                        operation_id
                    )
                )
                
                if status == "Succeeded":
                    TaskManager.update_progress(task_id, 90, "Translation completed. Generating download link...")
                    break
                elif status in ["Failed", "ValidationFailed", "Cancelled"]:
                    raise Exception(f"Translation failed with status: {status}")
                else:
                    # Running or NotStarted
                    TaskManager.update_progress(task_id, 50, f"Translating... ({status})")
                    await asyncio.sleep(2) # Poll every 2 seconds
            
            # 4. Generate Result Link
            # Note: We return a SAS URL so the frontend can download it directly from Azure Storage
            result_url = self.cloud_translator.storage.generate_blob_sas_url(
                container_name=self.cloud_translator.target_container,
                blob_name=filename
            )
            
            TaskManager.complete_task(task_id, {"download_url": result_url})
            
        except Exception as e:
            logger.error(f"Task {task_id} failed: {str(e)}")
            TaskManager.fail_task(task_id, str(e))

    async def translate_by_llm(self, 
                               file_content: bytes, 
                               filename: str, 
                               target_language: str, 
                               model: str = "gpt-4.1-mini",
                               translate_sheet_names: bool = False) -> io.BytesIO:
        """
        Translate a document using LLM-based chunk processing.
        
        Args:
            file_content: Raw bytes of the file.
            filename: Name of the file (to determine type).
            target_language: Target language (e.g., "English", "Chinese").
            model: Model name to use (e.g., "gpt-4.1-mini", "grok-3").
            
        Returns:
            io.BytesIO: Stream of the translated file.
        """
        file_obj = io.BytesIO(file_content)
        ext = filename.split('.')[-1].lower() if '.' in filename else ''

        # Define the translation callback used by parsers
        def translate_callback(text: str, context: str = None) -> str:
            return self._llm_translate_text(text, target_language, context, model)

        logger.info(f"Starting LLM translation for {filename} using model {model}")

        if ext == 'docx':
            return self.docx_parser.process(file_obj, translate_callback)
        elif ext == 'xlsx':
            return self.xlsx_parser.process(
                file_obj,
                lambda t: translate_callback(t),
                translate_sheet_names=translate_sheet_names
            )
        elif ext == 'pptx':
            return self.pptx_parser.process(file_obj, translate_callback)
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

    def _llm_translate_text(self, text: str, target_language: str, context: str = None, model: str = "gpt-4.1-mini") -> str:
        """
        Internal method to call the LLM service for a single text chunk.
        """
        # Construct system prompt
        system_content = (
            f"你是一个专业的翻译助手。请将用户提供的文本翻译成{target_language}。"
            "请注意保持翻译的专业性和准确性，并参考上下文, 不要丢失标点符号以及空格。"
        )
        messages = [{"role": "system", "content": system_content}]
        
        # Add context if available
        if context:
            messages.append({
                "role": "user", 
                "content": f"为了帮助你理解，这是该文本所在的完整段落上下文：\n---\n{context}\n---"
            })
            
        # Add text to translate
        messages.append({
            "role": "user", 
            "content": f"请仅翻译以下内容，不要添加任何额外的解释或标签：\n---\n{text}\n---"
        })
        
        try:
            # Call AzureLLMService
            response = self.llm_service.get_chat_completion(messages, model, stream=False)
            
            # Handle different response types (SDK vs REST/Requests)
            if hasattr(response, 'choices'): # OpenAI SDK Response
                return response.choices[0].message.content.strip()
            elif hasattr(response, 'json'): # Requests Response (REST)
                data = response.json()
                if 'choices' in data and len(data['choices']) > 0:
                    return data['choices'][0]['message']['content'].strip()
            
            logger.error(f"Unexpected response format from LLM service: {type(response)}")
            return text
            
        except Exception as e:
            logger.error(f"Translation failed for chunk: {text[:20]}... Error: {e}")
            return text # Return original text on failure
