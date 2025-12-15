from azure.storage.blob import (  
    BlobServiceClient, ContentSettings,  
    generate_container_sas, generate_blob_sas, BlobSasPermissions  
) 
from app_config.keys_config import (  
    AZURE_CONNECTION_STRING, AZURE_STORAGE_ACCOUNT_NAME,  
    AZURE_STORAGE_KEY, AZURE_STORAGE_ENDPOINT, AZURE_STORAGE_CONTAINER_NAME
)
from datetime import datetime, timedelta, timezone
from urllib.parse import quote  

class AzureBlobService:  
    def __init__(self):  
        self.connection_string = AZURE_CONNECTION_STRING  
        self.account_name = AZURE_STORAGE_ACCOUNT_NAME  
        self.account_key = AZURE_STORAGE_KEY  
        self.storage_endpoint = AZURE_STORAGE_ENDPOINT if AZURE_STORAGE_ENDPOINT.endswith('/') else AZURE_STORAGE_ENDPOINT + '/'  
  
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)  
  
    def ensure_container_exists(self, container_name):  
        container_client = self.blob_service_client.get_container_client(container_name)  
        if not container_client.exists():  
            container_client.create_container()  
        return container_client  
  
    def upload_file_to_blob_storage(self, file_name, file_obj):  
        container_client = self.ensure_container_exists(AZURE_STORAGE_CONTAINER_NAME)  
        # 推断content type  
        if file_name.lower().endswith(".pdf"):  
            content_type = "application/pdf"  
        elif file_name.lower().endswith(".docx"):  
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"  
        elif file_name.lower().endswith(".pptx"):  
            content_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"  
        elif file_name.lower().endswith(".txt"):  
            content_type = "text/plain"  
        else:  
            content_type = "application/octet-stream"  
        container_client.upload_blob(  
            name=file_name,  
            data=file_obj,  
            overwrite=True,  
            content_settings=ContentSettings(content_type=content_type)  
        )  
        blob_client = self.blob_service_client.get_blob_client(container=AZURE_STORAGE_CONTAINER_NAME, blob=file_name)  
        return blob_client.url  
  
    def generate_container_sas_url(self, container_name, permission, hours=2):  
        # permission：读源一般用'rl'，写目标一般用'wl'  

        start_time = datetime.now(timezone.utc)
        expiry_time = start_time + timedelta(hours=hours)

        sas_token = generate_container_sas(  
            account_name=self.account_name,  
            container_name=container_name,  
            account_key=self.account_key,  
            permission=permission,  
            start=start_time,
            expiry=expiry_time
        )  
        sas_url = f"{self.storage_endpoint}{container_name}?{sas_token}"  
        return sas_url  
    
    def generate_blob_sas_url(self, container_name, blob_name, hours=2):  
        """  
        生成指定blob的SAS访问链接。  
        :param container_name: 容器名  
        :param blob_name: blob路径/文件名  
        :param hours: 有效期（单位：小时）  
        :return: 带SAS的blob可访问URL  
        """  
        start_time = datetime.now(timezone.utc)  
        expiry_time = start_time + timedelta(hours=hours)  

        sas_token = generate_blob_sas(  
            account_name=self.account_name,  
            container_name=container_name,  
            blob_name=blob_name,  
            account_key=self.account_key,  
            permission=BlobSasPermissions(read=True), 
            start=start_time,  
            expiry=expiry_time  
        )  
        blob_url = f"{self.storage_endpoint}{container_name}/{blob_name}?{sas_token}"  
        new_url_plus = quote(blob_url, safe='/:?=&#%')
        return new_url_plus  