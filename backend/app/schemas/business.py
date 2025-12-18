from enum import Enum
from pydantic import BaseModel

class TranslationMode(str, Enum):
    CLOUD = "cloud"
    LOCAL = "local"

class TextTranslationRequest(BaseModel):
    text: str
    source_lang: str = "auto"
    target_lang: str

class TextTranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
