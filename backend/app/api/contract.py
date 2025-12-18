from fastapi import APIRouter, UploadFile, File, Depends, Form
from pydantic import BaseModel
from typing import List, Optional
from app.api import deps
from app.services.reviewer import ContractReviewer
import html
 
router = APIRouter(dependencies=[Depends(deps.get_current_user)])
reviewer = ContractReviewer()

class ReviewRequest(BaseModel):
    text: str

@router.post("/review/text")
def review_contract_text(body: ReviewRequest):
    analysis = reviewer.review_text(body.text)
    return {"analysis": analysis}

@router.post("/review/file")
async def review_contract_file(
    file: UploadFile = File(...),
    review_points: Optional[List[str]] = Form(None)
):
    content = await file.read()
    analysis = reviewer.review_document(content, review_points=review_points or None)
    return {"analysis": analysis}

@router.post("/review/bidding")
async def review_bidding(file: UploadFile = File(...)):
    content = await file.read()
    summary = reviewer.review_document(content)
    return {"analysis": summary}

@router.post("/diff")
async def contract_diff(
    file_original: UploadFile = File(...),
    file_revised: UploadFile = File(...)
):
    orig = await file_original.read()
    rev = await file_revised.read()
    try:
        t1 = orig.decode("utf-8", errors="ignore")
    except Exception:
        t1 = orig.decode("latin-1", errors="ignore")
    try:
        t2 = rev.decode("utf-8", errors="ignore")
    except Exception:
        t2 = rev.decode("latin-1", errors="ignore")
    safe_t1 = html.escape(t1[:4000])
    safe_t2 = html.escape(t2[:4000])
    html_diff = f"""
    <div style="font-family: sans-serif;">
      <h3>原始版本预览</h3>
      <pre style="background:#f7f7f7;padding:12px;border:1px solid #ddd;white-space:pre-wrap;">{safe_t1}</pre>
      <h3>修订版本预览</h3>
      <pre style="background:#f7f7f7;padding:12px;border:1px solid #ddd;white-space:pre-wrap;">{safe_t2}</pre>
      <p style="color:#888;">提示：如需字词级修订高亮，请在后端启用 mammoth + jieba 的深度比对。</p>
    </div>
    """
    return {"html_diff": html_diff}
