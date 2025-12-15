"""
Request Models (Pydantic)
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


# ========== Authentication ==========
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


# ========== Translation ==========
class LanguageEnum(str, Enum):
    ZH_CN = "zh-Hans"
    ZH_TW = "zh-Hant"
    EN = "en"
    JA = "ja"
    KO = "ko"
    FR = "fr"
    DE = "de"
    ES = "es"


class TranslateRequest(BaseModel):
    text: str = Field(..., max_length=10000)
    source_lang: LanguageEnum
    target_lang: LanguageEnum
    use_cloud: bool = Field(default=True, description="Use cloud Azure translation or local model")


class DocumentTranslateRequest(BaseModel):
    source_lang: LanguageEnum
    target_lang: LanguageEnum
    use_cloud: bool = Field(default=True)


# ========== Document Review ==========
class ContractReviewRequest(BaseModel):
    analysis_type: str = Field(default="comprehensive", description="comprehensive, risk, compliance")


class BiddingReviewRequest(BaseModel):
    check_compliance: bool = Field(default=True)
    check_completeness: bool = Field(default=True)


class DocumentCompareRequest(BaseModel):
    compare_mode: str = Field(default="detailed", description="detailed, summary")


# ========== Chat ==========
class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000)
    model: Optional[str] = Field(default="gpt-4", description="Model to use")
    history: Optional[List[ChatMessage]] = Field(default=[])
    stream: bool = Field(default=False)
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=2000, gt=0)


class MultimodalChatRequest(BaseModel):
    message: str
    image_urls: Optional[List[str]] = Field(default=[])
    model: Optional[str] = Field(default="gpt-4-vision")
    history: Optional[List[ChatMessage]] = Field(default=[])


# ========== Dify Integration ==========
class DifyChatRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = None
    user_id: str = Field(default="default_user")


# ========== Image Recognition ==========
class ImageDetectionRequest(BaseModel):
    detection_type: str = Field(default="violation", description="violation type to detect")
    confidence_threshold: float = Field(default=0.7, ge=0, le=1)


# ========== BI Query ==========
class BIQueryRequest(BaseModel):
    question: str = Field(..., description="Natural language question")
    database: Optional[str] = Field(default=None, description="Target database")


# ========== Case Study ==========
class CaseSearchRequest(BaseModel):
    keyword: str
    filters: Optional[dict] = Field(default={})
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class CustomerResearchRequest(BaseModel):
    customer_name: str
    research_depth: str = Field(default="standard", pattern="^(basic|standard|deep)$")


# ========== Settings ==========
class PromptConfigUpdate(BaseModel):
    prompt_name: str
    prompt_content: str
    description: Optional[str] = None


class NewsletterSettingsUpdate(BaseModel):
    enabled: bool = Field(default=True)
    frequency: str = Field(default="daily", pattern="^(daily|weekly|monthly)$")
    recipients: List[str] = Field(default=[])
