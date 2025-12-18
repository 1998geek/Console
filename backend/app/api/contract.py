from fastapi import APIRouter, UploadFile, File, Depends
from pydantic import BaseModel
from app.api import deps
from app.services.reviewer import ContractReviewer

router = APIRouter(dependencies=[Depends(deps.get_current_user)])
reviewer = ContractReviewer()

class ReviewRequest(BaseModel):
    text: str

@router.post("/review/text")
def review_contract_text(body: ReviewRequest):
    analysis = reviewer.review_text(body.text)
    return {"analysis": analysis}

@router.post("/review/file")
async def review_contract_file(file: UploadFile = File(...)):
    content = await file.read()
    analysis = reviewer.review_document(content)
    return {"analysis": analysis}
