# https://learn.microsoft.com/en-us/azure/ai-services/translator/service-limits
# Asynchronous (batch) operation limits
# Attribute	Limit
# Document size	≤ 40 MB
# Total number of files.	≤ 1000
# Total content size in a batch	≤ 250 MB
# Number of target languages in a batch	≤ 10
# Size of glossary file	≤ 10 MB

from azure.core.credentials import AzureKeyCredential  
from azure.ai.translation.document import (  
    DocumentTranslationClient, DocumentTranslationInput, TranslationTarget  
) 
from app_config.keys_config import (  
    AZURE_DOCUMENT_TRANSLATION_ENDPOINT,  
    AZURE_DOCUMENT_TRANSLATION_KEY,  
    AZURE_STORAGE_CONTAINER_NAME,  
    AZURE_TARGET_CONTAINER_NAME,  
)  
from function.AzureBlobService import AzureBlobService  # 替换为你的 storage 类路径  
  
class AzureDocumentTranslator:  
    def __init__(self):  
        self.endpoint = AZURE_DOCUMENT_TRANSLATION_ENDPOINT  
        self.key = AZURE_DOCUMENT_TRANSLATION_KEY  
        self.source_container = AZURE_STORAGE_CONTAINER_NAME  
        self.target_container = AZURE_TARGET_CONTAINER_NAME  
        self.storage = AzureBlobService()  # Storage 依赖注入，可传入或内部new  
  
    def ensure_containers(self):  
        self.storage.ensure_container_exists(self.source_container)  
        self.storage.ensure_container_exists(self.target_container)  
      
    def start_translation(self, file_name_or_prefix, to_language='zh'):  
        self.ensure_containers()  
        # 生成SAS地址  
        source_sas_url = self.storage.generate_container_sas_url(self.source_container, permission='rl')  
        target_sas_url = self.storage.generate_container_sas_url(self.target_container, permission='wl')  
  
        translation_client = DocumentTranslationClient(  
            self.endpoint,  
            AzureKeyCredential(self.key)  
        )  
  
  
        # 指定只翻译当前文件（通常源容器下有很多文件，通过filter/prefix精确指定）  
        inputs = [  
            DocumentTranslationInput(  
                source_url=source_sas_url,  
                targets=[TranslationTarget(target_url=target_sas_url, language=to_language)],  
                prefix=file_name_or_prefix  
            )  
        ]  

        poller = translation_client.begin_translation(inputs=inputs)  
        
        # 等待并获取结果  
        for document in poller.result():  
            if document.status == "Succeeded":  
                return self.storage.generate_blob_sas_url(
                    container_name=self.target_container,
                    blob_name=file_name_or_prefix)
                # return document.translated_document_url  
            elif document.error:  
                raise Exception(f"Document translation failed: {document.error.code} {document.error.message}")  
  
        raise Exception("No successful translation found.")  
  