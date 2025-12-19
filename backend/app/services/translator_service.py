from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import (
    DocumentTranslationClient, DocumentTranslationInput, TranslationTarget
)
from app.core.config import settings
from app.services.blob_service import AzureBlobService
from utils.redis_client import redis_client
import time

class AzureDocumentTranslator:
    def __init__(self):
        self.endpoint = settings.AZURE_DOCUMENT_TRANSLATION_ENDPOINT
        self.key = settings.AZURE_DOCUMENT_TRANSLATION_KEY
        self.source_container = settings.AZURE_STORAGE_CONTAINER_NAME
        self.target_container = settings.AZURE_TARGET_CONTAINER_NAME
        self.storage = AzureBlobService()
        
        self.client = DocumentTranslationClient(
            self.endpoint,
            AzureKeyCredential(self.key)
        )

    def start_translation_job(self, blob_name: str, to_language: str = 'zh'):
        self.storage.ensure_container_exists(self.source_container)
        self.storage.ensure_container_exists(self.target_container)

        source_sas_url = self.storage.generate_container_sas_url(self.source_container, permission='rl')
        target_sas_url = self.storage.generate_container_sas_url(self.target_container, permission='wl')

        inputs = [
            DocumentTranslationInput(
                source_url=source_sas_url,
                targets=[TranslationTarget(target_url=target_sas_url, language=to_language)],
                prefix=blob_name
            )
        ]
        
        poller = self.client.begin_translation(inputs=inputs)
        return poller

def background_track_translation(task_id: str, blob_name: str, translator: AzureDocumentTranslator, poller):
    try:
        redis_client.set_task_progress(task_id, 10, "任务已提交至 Azure (初始化中)...", "processing")
        
        # 阻塞等待结果 (Azure 处理时间)
        result_iterator = poller.result() 
        
        redis_client.set_task_progress(task_id, 90, "Azure 处理完成，正在生成下载链接...", "processing")

        succeeded = False
        error_msg = ""
        
        for document in result_iterator:
            if document.status == "Succeeded":
                succeeded = True
            elif document.error:
                error_msg = f"{document.error.code}: {document.error.message}"
        
        if succeeded:
            # 生成下载链接
            download_url = translator.storage.generate_blob_sas_url(
                container_name=settings.AZURE_TARGET_CONTAINER_NAME,
                blob_name=blob_name
            )
            # [DEBUG LOG] 打印生成的链接
            print(f"✅ Task {task_id} Success. URL: {download_url}")
            
            redis_client.set_task_progress(task_id, 100, "翻译成功", "completed", download_url)
        else:
            print(f"❌ Task {task_id} Failed on Azure: {error_msg}")
            redis_client.set_task_progress(task_id, 0, f"翻译失败: {error_msg}", "failed")
            
    except Exception as e:
        print(f"❌ Task {task_id} System Error: {e}")
        redis_client.set_task_progress(task_id, 0, f"系统错误: {str(e)}", "failed")
