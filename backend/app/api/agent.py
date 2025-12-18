from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api import deps
from app.services.dify_service import DifyService

router = APIRouter(dependencies=[Depends(deps.get_current_user)])
dify = DifyService()

class ChatRequest(BaseModel):
    query: str
    conversation_id: str | None = None
    inputs: dict | None = None

@router.post("/dify/chat")
def dify_chat(body: ChatRequest, current_user=Depends(deps.get_current_user)):
    user_id = getattr(current_user, "username", None) or getattr(current_user, "id", "unknown")
    result = dify.chat(query=body.query, user=str(user_id), conversation_id=body.conversation_id, inputs=body.inputs or {})
    return result
