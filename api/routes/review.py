"""
Document Review Routes - Contract & Bidding Document Review
"""
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from ..models.request import ContractReviewRequest, BiddingReviewRequest, DocumentCompareRequest
from ..models.response import (
    ContractReviewResponse, 
    BiddingReviewResponse,
    DocumentCompareResponse,
    DataResponse,
    RiskItem
)
from ..core.security import get_current_user
from ..utils.helpers import save_upload_file, cleanup_file

router = APIRouter(prefix="/review", tags=["Document Review"])


def mock_contract_review(file_path: str, analysis_type: str) -> ContractReviewResponse:
    """Mock contract review logic"""
    # In production, integrate with your AI contract review logic
    risks = [
        RiskItem(
            category="Payment Terms",
            severity="high",
            description="Payment schedule lacks clear milestone definitions",
            location="Section 3.2",
            suggestion="Add specific milestone deliverables and payment triggers"
        ),
        RiskItem(
            category="Liability",
            severity="medium",
            description="Liability cap may be insufficient for project scope",
            location="Section 7.1",
            suggestion="Review and adjust liability limits based on project value"
        ),
        RiskItem(
            category="Termination",
            severity="low",
            description="Termination notice period is shorter than industry standard",
            location="Section 9.3",
            suggestion="Consider extending notice period to 30 days"
        )
    ]
    
    suggestions = [
        "Add force majeure clause with detailed examples",
        "Include intellectual property rights section",
        "Specify governing law and dispute resolution mechanism"
    ]
    
    return ContractReviewResponse(
        overall_score=72.5,
        risk_level="medium",
        risks=risks,
        suggestions=suggestions,
        summary="The contract has been reviewed and contains some areas requiring attention. "
                "Primary concerns include payment term clarity and liability coverage. "
                "Overall structure is sound but could benefit from additional protective clauses."
    )


def mock_bidding_review(file_path: str, check_compliance: bool, check_completeness: bool) -> BiddingReviewResponse:
    """Mock bidding document review logic"""
    issues = [
        {
            "type": "compliance",
            "severity": "high",
            "description": "Missing required ISO 9001 certification documentation"
        },
        {
            "type": "completeness",
            "severity": "medium",
            "description": "Project timeline lacks detailed task breakdown"
        }
    ]
    
    missing_items = [
        "Company registration certificate",
        "Financial audit report for last 3 years",
        "Technical team CVs and certifications"
    ]
    
    recommendations = [
        "Add detailed technical implementation plan",
        "Include risk mitigation strategies",
        "Provide reference projects with similar scope",
        "Clarify after-sales service and warranty terms"
    ]
    
    return BiddingReviewResponse(
        compliance_passed=False,
        completeness_score=68.0,
        issues=issues,
        missing_items=missing_items,
        recommendations=recommendations
    )


def mock_document_compare(file1_path: str, file2_path: str, compare_mode: str) -> DocumentCompareResponse:
    """Mock document comparison logic"""
    differences = [
        {
            "type": "content_changed",
            "location": "Section 2, Paragraph 3",
            "old_content": "Payment due within 30 days",
            "new_content": "Payment due within 45 days",
            "significance": "high"
        },
        {
            "type": "content_added",
            "location": "Section 5.2",
            "new_content": "Additional clause regarding intellectual property rights",
            "significance": "medium"
        },
        {
            "type": "content_deleted",
            "location": "Section 7.1",
            "old_content": "Penalty clause for late delivery",
            "significance": "high"
        }
    ]
    
    return DocumentCompareResponse(
        differences=differences,
        similarity_score=87.3,
        summary="Documents are largely similar with 3 significant changes detected. "
                "Key differences include modified payment terms and removal of penalty clause. "
                "Recommend careful review of deleted penalty provisions."
    )


@router.post("/contract", response_model=DataResponse)
async def review_contract(
    file: UploadFile = File(..., description="Contract document to review"),
    analysis_type: str = "comprehensive",
    current_user: dict = Depends(get_current_user)
):
    """
    Intelligent contract review
    
    Upload a contract document for AI-powered analysis
    
    - **file**: Contract document (.docx, .pdf)
    - **analysis_type**: Type of analysis (comprehensive, risk, compliance)
    
    Returns risk assessment, suggestions, and overall score
    """
    # Save file
    file_path = await save_upload_file(file)
    
    try:
        # Perform review
        result = mock_contract_review(file_path, analysis_type)
        
        return DataResponse(
            code=200,
            message="Contract review completed",
            data=result.dict()
        )
    finally:
        # Cleanup
        cleanup_file(file_path)


@router.post("/bidding", response_model=DataResponse)
async def review_bidding_document(
    file: UploadFile = File(..., description="Bidding document to review"),
    check_compliance: bool = True,
    check_completeness: bool = True,
    current_user: dict = Depends(get_current_user)
):
    """
    Intelligent bidding document review
    
    Upload a bidding document for compliance and completeness check
    
    - **file**: Bidding document (.docx, .pdf)
    - **check_compliance**: Check compliance with requirements
    - **check_completeness**: Check document completeness
    
    Returns compliance status, missing items, and recommendations
    """
    # Save file
    file_path = await save_upload_file(file)
    
    try:
        # Perform review
        result = mock_bidding_review(file_path, check_compliance, check_completeness)
        
        return DataResponse(
            code=200,
            message="Bidding document review completed",
            data=result.dict()
        )
    finally:
        # Cleanup
        cleanup_file(file_path)


@router.post("/compare", response_model=DataResponse)
async def compare_documents(
    file1: UploadFile = File(..., description="First document"),
    file2: UploadFile = File(..., description="Second document"),
    compare_mode: str = "detailed",
    current_user: dict = Depends(get_current_user)
):
    """
    Compare two documents and identify differences
    
    Upload two documents to compare and get detailed difference analysis
    
    - **file1**: First document (.docx)
    - **file2**: Second document (.docx)
    - **compare_mode**: Comparison mode (detailed, summary)
    
    Returns list of differences, similarity score, and summary
    """
    # Save files
    file1_path = await save_upload_file(file1, "doc1_" + file1.filename)
    file2_path = await save_upload_file(file2, "doc2_" + file2.filename)
    
    try:
        # Perform comparison
        result = mock_document_compare(file1_path, file2_path, compare_mode)
        
        return DataResponse(
            code=200,
            message="Document comparison completed",
            data=result.dict()
        )
    finally:
        # Cleanup
        cleanup_file(file1_path)
        cleanup_file(file2_path)
