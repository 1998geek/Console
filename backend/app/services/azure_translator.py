from datetime import datetime, timedelta, timezone
from urllib.parse import quote
from azure.storage.blob import (
    BlobServiceClient, ContentSettings,
    generate_container_sas, generate_blob_sas, BlobSasPermissions
)
from azure.core.credentials import AzureKeyCredential
from azure.ai.translation.document import (
    DocumentTranslationClient, DocumentTranslationInput, TranslationTarget
)
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class AzureStorageService:
    """Helper service for Azure Blob Storage operations."""
    def __init__(self):
        self.connection_string = settings.AZURE_CONNECTION_STRING
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        self.account_key = settings.AZURE_STORAGE_KEY
        self.storage_endpoint = settings.AZURE_STORAGE_ENDPOINT
        
        if self.storage_endpoint and not self.storage_endpoint.endswith('/'):
            self.storage_endpoint += '/'

        if self.connection_string:
            self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        else:
            logger.warning("Azure Storage connection string is missing.")
            self.blob_service_client = None

    def ensure_container_exists(self, container_name: str):
        if not self.blob_service_client:
            raise Exception("BlobServiceClient not initialized")
        
        container_client = self.blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()
        return container_client

    def generate_container_sas_url(self, container_name: str, permission: str, hours: int = 2) -> str:
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

    def generate_blob_sas_url(self, container_name: str, blob_name: str, hours: int = 2) -> str:
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
        # URL encode to be safe
        return quote(blob_url, safe='/:?=&#%')

    def upload_blob(self, container_name: str, blob_name: str, data: bytes):
        if not self.blob_service_client:
            raise Exception("BlobServiceClient not initialized")
        
        container_client = self.blob_service_client.get_container_client(container_name)
        if not container_client.exists():
            container_client.create_container()
            
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(data, overwrite=True)

    def download_blob(self, container_name: str, blob_name: str) -> bytes:
        if not self.blob_service_client:
            raise Exception("BlobServiceClient not initialized")
            
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(blob_name)
        
        if not blob_client.exists():
            raise Exception(f"Blob {blob_name} does not exist in container {container_name}")
            
        return blob_client.download_blob().readall()

class AzureDocumentTranslator:
    """
    Service for Azure Document Translation.
    Migrated from legacy AzureDocumentTranslator.
    """
    def __init__(self):
        self.endpoint = settings.AZURE_DOCUMENT_TRANSLATION_ENDPOINT
        self.key = settings.AZURE_DOCUMENT_TRANSLATION_KEY
        self.source_container = settings.AZURE_STORAGE_CONTAINER_NAME
        self.target_container = settings.AZURE_TARGET_CONTAINER_NAME
        self.storage = AzureStorageService()

    def ensure_containers(self):
        self.storage.ensure_container_exists(self.source_container)
        self.storage.ensure_container_exists(self.target_container)

    def check_target_exists(self, filename: str) -> bool:
        """Check if the target file already exists in the target container."""
        try:
            target_blob_client = self.storage.blob_service_client.get_blob_client(
                container=self.target_container, 
                blob=filename
            )
            return target_blob_client.exists()
        except Exception as e:
            logger.warning(f"Failed to check target existence: {e}")
            return False

    def start_translation_async(self, file_name_or_prefix: str, to_language: str = 'zh') -> str:
        """
        Starts document translation asynchronously and returns the operation ID (not waiting for completion).
        """
        self.ensure_containers()
        
        # Generate SAS URLs
        source_sas_url = self.storage.generate_container_sas_url(self.source_container, permission='rl')
        target_sas_url = self.storage.generate_container_sas_url(self.target_container, permission='wl')

        translation_client = DocumentTranslationClient(
            self.endpoint,
            AzureKeyCredential(self.key)
        )

        inputs = [
            DocumentTranslationInput(
                source_url=source_sas_url,
                targets=[TranslationTarget(target_url=target_sas_url, language=to_language)],
                prefix=file_name_or_prefix
            )
        ]

        try:
            # begin_translation returns a poller. We can get the ID from it.
            poller = translation_client.begin_translation(inputs=inputs)
            # The operation ID is usually part of the polling URL or details.
            # In Azure SDK, poller.details['id'] usually holds the operation ID.
            return poller.id
        except Exception as e:
            logger.error(f"Async document translation error: {str(e)}")
            raise e

    def check_translation_status(self, operation_id: str) -> str:
        """
        Checks the status of a translation operation.
        Returns: 'NotStarted', 'Running', 'Succeeded', 'Failed', 'Cancelled', 'ValidationFailed'
        """
        translation_client = DocumentTranslationClient(
            self.endpoint,
            AzureKeyCredential(self.key)
        )
        
        try:
            status = translation_client.get_translation_status(operation_id)
            return status.status
        except Exception as e:
            logger.error(f"Error checking translation status: {str(e)}")
            raise e

    def start_translation(self, file_name_or_prefix: str, to_language: str = 'zh') -> str:
        """
        Starts document translation and returns the result SAS URL.
        """
        self.ensure_containers()
        
        # Generate SAS URLs
        source_sas_url = self.storage.generate_container_sas_url(self.source_container, permission='rl')
        target_sas_url = self.storage.generate_container_sas_url(self.target_container, permission='wl')

        # Check if target file already exists
        try:
            # Note: Azure Translation Service usually names the target file same as source file (or using prefix)
            # If we can check if the blob exists, we can return early.
            # The file name in target container is 'file_name_or_prefix' because we used it as prefix and it's a single file.
            # However, translation service might append language code if not specified? 
            # Usually with 'prefix' input, it keeps the name.
            
            # Let's check if the blob exists in the target container
            target_blob_client = self.storage.blob_service_client.get_blob_client(
                container=self.target_container, 
                blob=file_name_or_prefix
            )
            
            if target_blob_client.exists():
                logger.info(f"Target file {file_name_or_prefix} already exists. Returning existing file.")
                return self.storage.generate_blob_sas_url(
                    container_name=self.target_container,
                    blob_name=file_name_or_prefix
                )
        except Exception as check_ex:
            logger.warning(f"Failed to check if target blob exists: {check_ex}")
            # Continue to translation if check fails

        translation_client = DocumentTranslationClient(
            self.endpoint,
            AzureKeyCredential(self.key)
        )

        inputs = [
            DocumentTranslationInput(
                source_url=source_sas_url,
                targets=[TranslationTarget(target_url=target_sas_url, language=to_language)],
                prefix=file_name_or_prefix
            )
        ]

        try:
            poller = translation_client.begin_translation(inputs=inputs)
            
            # Wait for result
            for document in poller.result():
                if document.status == "Succeeded":
                    # Return SAS URL for the translated file
                    # Note: The translated file usually has the same name in target container
                    return self.storage.generate_blob_sas_url(
                        container_name=self.target_container,
                        blob_name=file_name_or_prefix
                    )
                elif document.error:
                    raise Exception(f"Translation failed: {document.error.code} {document.error.message}")
            
            raise Exception("No successful translation found.")

        except Exception as e:
            logger.error(f"Document translation error: {str(e)}")
            raise e
