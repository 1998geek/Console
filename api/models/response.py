"""
Response Models (Pydantic)
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime
from enum import Enum


class StatusEnum(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PROCESSING = "processing"
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class BaseResponse(BaseModel):
    """Base response model"""
    code: int = Field(default=200)
    message: str = Field(default="success")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DataResponse(BaseResponse):
    """Response with data"""
    data: Optional[Any] = None


class ErrorResponse(BaseResponse):
    """Error response"""
    code: int = Field(default=400)
    message: str = Field(default="error")
    error: Optional[str] = None


# ========== Authentication ==========
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(default=86400, description="Seconds until expiration")


class UserInfo(BaseModel):
    username: str
    is_admin: bool = False
    created_at: Optional[datetime] = None


# ========== Translation ==========
class TranslateResponse(BaseModel):
    translated_text: str
    source_lang: str
    target_lang: str
    char_count: int


class TaskResponse(BaseModel):
    task_id: str
    status: StatusEnum
    message: str = "Task created successfully"


class TaskStatusResponse(BaseModel):
    task_id: str
    status: StatusEnum
    progress: Optional[float] = Field(default=0, ge=0, le=100)
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ========== Document Review ==========
class RiskItem(BaseModel):
    category: str
    severity: str  # low, medium, high, critical
    description: str
    location: Optional[str] = None
    suggestion: Optional[str] = None


class ContractReviewResponse(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    risk_level: str  # low, medium, high
    risks: List[RiskItem]
    suggestions: List[str]
    summary: str


class BiddingReviewResponse(BaseModel):
    compliance_passed: bool
    completeness_score: float = Field(..., ge=0, le=100)
    issues: List[Dict[str, str]]
    missing_items: List[str]
    recommendations: List[str]


class DocumentCompareResponse(BaseModel):
    differences: List[Dict[str, Any]]
    similarity_score: float = Field(..., ge=0, le=100)
    summary: str


# ========== Chat ==========
class ChatResponse(BaseModel):
    response: str
    model: str
    usage: Optional[Dict[str, int]] = None


class MultimodalChatResponse(BaseModel):
    response: str
    model: str
    images_processed: int


# ========== Image Recognition ==========
class DetectionResult(BaseModel):
    label: str
    confidence: float = Field(..., ge=0, le=1)
    bbox: Optional[List[float]] = None
    description: Optional[str] = None


class ImageDetectionResponse(BaseModel):
    detections: List[DetectionResult]
    image_url: Optional[str] = None
    annotated_image_url: Optional[str] = None


# ========== BI Query ==========
class BIQueryResponse(BaseModel):
    sql_query: str
    results: List[Dict[str, Any]]
    row_count: int
    chart_data: Optional[Dict[str, Any]] = None
    explanation: str


# ========== Case Study ==========
class CaseItem(BaseModel):
    case_id: str
    title: str
    summary: str
    relevance_score: float
    created_at: datetime


class CaseSearchResponse(BaseModel):
    cases: List[CaseItem]
    total: int
    page: int
    page_size: int


class CustomerResearchResponse(BaseModel):
    customer_name: str
    industry: Optional[str] = None
    company_size: Optional[str] = None
    financial_status: Optional[str] = None
    risk_assessment: Optional[str] = None
    key_insights: List[str]
    sources: List[str]


# ========== Settings ==========
class PromptConfig(BaseModel):
    id: str
    prompt_name: str
    prompt_content: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class NewsletterSettings(BaseModel):
    enabled: bool
    frequency: str
    recipients: List[str]
    last_sent: Optional[datetime] = None
