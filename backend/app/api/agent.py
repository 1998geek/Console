from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.api import deps
from app.services.dify_service import DifyService
from app.services.azure_ai import AzureLLMService
from app.core.config import settings
import requests
import json

router = APIRouter(dependencies=[Depends(deps.get_current_user)])
dify = DifyService()
llm_service = AzureLLMService()

class ChatRequest(BaseModel):
    query: str
    conversation_id: str | None = None
    inputs: dict | None = None

@router.post("/dify/chat")
def dify_chat(body: ChatRequest, current_user=Depends(deps.get_current_user)):
    user_id = getattr(current_user, "username", None) or getattr(current_user, "id", "unknown")
    result = dify.chat(query=body.query, user=str(user_id), conversation_id=body.conversation_id, inputs=body.inputs or {})
    return result

class XinferenceChatRequest(BaseModel):
    model: str
    messages: list[dict]
    show_thinking: bool = False

@router.post("/xinference/chat")
def xinference_chat(body: XinferenceChatRequest, current_user=Depends(deps.get_current_user)):
    base = settings.XINFERENCE_BASE_URL.strip()
    if base:
        url = f"{base.rstrip('/')}/v1/chat/completions"
        payload = {"model": body.model, "messages": body.messages, "stream": True}
        headers = {"Content-Type": "application/json"}
        resp = requests.post(url, json=payload, headers=headers, stream=True, timeout=120)
        def gen_xinference():
            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    data_str = line.decode("utf-8")
                    # print(f"DEBUG Xinference line: {data_str}") # Debug log
                    if data_str.startswith("data: "):
                        data_str = data_str[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    
                    # Handle empty data strings that might occur after stripping "data: "
                    if not data_str.strip():
                        continue
                        
                    obj = json.loads(data_str)
                    if obj.get("choices"):
                        delta = obj["choices"][0].get("delta", {})
                        content = delta.get("content")
                        if content:
                            yield content
                except Exception as e:
                    print(f"Error parsing xinference stream: {e}, line: {line}")
                    continue
        return StreamingResponse(gen_xinference(), media_type="text/plain")
    else:
        model_map = {
            "qwen3": "gpt-4.1-mini",
            "qwen2.5-vl-instruct": "gpt-4o-mini",
        }
        target_model = model_map.get(body.model, "gpt-4.1-mini")
        response = llm_service.get_chat_completion(body.messages, model=target_model, stream=True)
        def gen():
            for token in AzureLLMService.stream_processor(response):
                yield token
        return StreamingResponse(gen(), media_type="text/plain")

class MultimodalChatRequest(BaseModel):
    model: str
    messages: list[dict]

@router.post("/multimodal/chat")
def multimodal_chat(body: MultimodalChatRequest, current_user=Depends(deps.get_current_user)):
    response = llm_service.get_chat_completion(body.messages, model=body.model, stream=True)
    def gen():
        for token in AzureLLMService.stream_processor(response):
            yield token
    return StreamingResponse(gen(), media_type="text/plain")
