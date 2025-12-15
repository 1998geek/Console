"""
Translation Service
Integrates with existing translation functionality
"""
import sys
import os

# Add parent directory to path to import function modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from typing import Optional
from function.AzureDocumentTranslator import AzureDocumentTranslator


class TranslationService:
    """Translation service using Azure or local models"""
    
    def __init__(self):
        self.azure_translator = None
        try:
            self.azure_translator = AzureDocumentTranslator()
        except Exception as e:
            print(f"Warning: Azure translator not initialized: {e}")
    
    async def translate_text(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str,
        use_cloud: bool = True
    ) -> dict:
        """
        Translate text using Azure Translation or local model
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            use_cloud: Use Azure cloud service (True) or local model (False)
        
        Returns:
            dict with translated_text, source_lang, target_lang, char_count
        """
        if use_cloud and self.azure_translator:
            try:
                # Use Azure Translation
                result = await self._translate_with_azure(text, source_lang, target_lang)
                return result
            except Exception as e:
                print(f"Azure translation failed: {e}, falling back to mock")
                return self._mock_translation(text, source_lang, target_lang)
        else:
            # Use local model (mock for now)
            return self._mock_translation(text, source_lang, target_lang)
    
    async def _translate_with_azure(self, text: str, source_lang: str, target_lang: str) -> dict:
        """Use Azure Translation API"""
        # This would integrate with your existing AzureDocumentTranslator
        # For now, return mock data
        return self._mock_translation(text, source_lang, target_lang)
    
    def _mock_translation(self, text: str, source_lang: str, target_lang: str) -> dict:
        """Mock translation for demo purposes"""
        # Simple mock: just add [TRANSLATED] prefix
        translated_text = f"[TRANSLATED from {source_lang} to {target_lang}] {text}"
        
        return {
            "translated_text": translated_text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "char_count": len(text)
        }
    
    async def translate_document(
        self,
        file_path: str,
        source_lang: str,
        target_lang: str,
        use_cloud: bool = True
    ) -> str:
        """
        Translate a document file
        
        Args:
            file_path: Path to document file
            source_lang: Source language code
            target_lang: Target language code
            use_cloud: Use Azure cloud service or local model
        
        Returns:
            Path to translated document
        """
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if use_cloud and self.azure_translator:
            # Use Azure Document Translation
            try:
                output_path = file_path.replace(file_ext, f"_translated{file_ext}")
                # This would use your existing Azure translation logic
                # For demo, just copy the file
                import shutil
                shutil.copy(file_path, output_path)
                return output_path
            except Exception as e:
                raise Exception(f"Document translation failed: {e}")
        else:
            # Use local translation (would integrate with local models)
            output_path = file_path.replace(file_ext, f"_translated{file_ext}")
            import shutil
            shutil.copy(file_path, output_path)
            return output_path


# Global service instance
translation_service = TranslationService()
