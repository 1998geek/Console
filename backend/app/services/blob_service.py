from azure.storage.blob import (
    BlobServiceClient, ContentSettings,
    generate_container_sas, generate_blob_sas, BlobSasPermissions
)
from app.core.config import settings
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
import uuid
import os

class AzureBlobService:
    def __init__(self):
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        self.account_key = settings.AZURE_STORAGE_KEY
        
        # 处理 Endpoint 格式，确保结尾有 '/'
        ep = settings.AZURE_STORAGE_ENDPOINT
        self.storage_endpoint = ep if ep.endswith('/') else ep + '/'

    def ensure_container_exists(self, container_name):
        container_client = self.blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()
        return container_client

    def upload_file(self, file_content: bytes, original_filename: str) -> str:
        """
        上传文件并返回 Blob 名称 (Path)
        """
        # 生成唯一文件名: files/uuid_filename
        unique_name = f"files/{uuid.uuid4()}_{original_filename}"
        
        container_client = self.ensure_container_exists(settings.AZURE_STORAGE_CONTAINER_NAME)
        
        # 推断 Content Type
        content_type = "application/octet-stream"
        if original_filename.lower().endswith(".pdf"):
            content_type = "application/pdf"
        elif original_filename.lower().endswith(".docx"):
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        
        # 上传
        container_client.upload_blob(
            name=unique_name,
            data=file_content,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type)
        )
        return unique_name

    def generate_container_sas_url(self, container_name, permission, hours=2):
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
        return f"{self.storage_endpoint}{container_name}?{sas_token}"

    def generate_blob_sas_url(self, container_name, blob_name, hours=24):
        """生成带 SAS 的下载链接"""
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
        # URL 编码处理特殊字符
        return quote(blob_url, safe='/:?=&#%')
