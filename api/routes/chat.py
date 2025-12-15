"""
Chat Routes - AI Conversation APIs
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from ..models.request import ChatRequest, MultimodalChatRequest
from ..models.response import ChatResponse, MultimodalChatResponse, DataResponse
from ..core.security import get_current_user
import json
import asyncio

router = APIRouter(prefix="/chat", tags=["Chat"])


async def mock_ai_response(message: str, model: str) -> str:
    """Mock AI response generator"""
    # In production, integrate with OpenAI, Azure OpenAI, or other LLM providers
    responses = {
        "gpt-4": f"[GPT-4 Response] I understand you said: '{message}'. This is a mock response from the API.",
        "gpt-3.5-turbo": f"[GPT-3.5 Response] Based on your message: '{message}', here's my response.",
        "claude": f"[Claude Response] Thank you for your message: '{message}'. Here's what I think..."
    }
    return responses.get(model, f"[{model}] Response to: {message}")


async def stream_ai_response(message: str, model: str):
    """Stream AI response token by token"""
    response = await mock_ai_response(message, model)
    words = response.split()
    
    for word in words:
        yield f"data: {json.dumps({'token': word + ' '})}\n\n"
        await asyncio.sleep(0.05)  # Simulate streaming delay
    
    yield f"data: {json.dumps({'done': True})}\n\n"


@router.post("/completion", response_model=DataResponse)
async def chat_completion(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Chat completion with AI models
    
    - **message**: User message
    - **model**: AI model to use (gpt-4, gpt-3.5-turbo, claude, etc.)
    - **history**: Conversation history (optional)
    - **stream**: Enable streaming response (use /chat/stream for streaming)
    - **temperature**: Creativity level (0.0 - 2.0)
    - **max_tokens**: Maximum response length
    """
    if request.stream:
        raise HTTPException(
            status_code=400,
            detail="For streaming responses, use the /chat/stream endpoint"
        )
    
    # Generate AI response
    response_text = await mock_ai_response(request.message, request.model)
    
    chat_response = ChatResponse(
        response=response_text,
        model=request.model,
        usage={
            "prompt_tokens": len(request.message.split()),
            "completion_tokens": len(response_text.split()),
            "total_tokens": len(request.message.split()) + len(response_text.split())
        }
    )
    
    return DataResponse(
        code=200,
        message="Chat completion successful",
        data=chat_response.dict()
    )


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Streaming chat completion
    
    Returns Server-Sent Events (SSE) stream
    
    - **message**: User message
    - **model**: AI model to use
    - **history**: Conversation history (optional)
    """
    return StreamingResponse(
        stream_ai_response(request.message, request.model),
        media_type="text/event-stream"
    )


@router.post("/multimodal", response_model=DataResponse)
async def multimodal_chat(
    request: MultimodalChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Multimodal chat (text + images)
    
    - **message**: User message
    - **image_urls**: List of image URLs to analyze
    - **model**: Vision-capable AI model (gpt-4-vision, gemini-pro-vision, etc.)
    - **history**: Conversation history (optional)
    """
    # Mock multimodal response
    images_count = len(request.image_urls) if request.image_urls else 0
    response_text = f"[{request.model}] I see {images_count} image(s). Regarding your question: '{request.message}', here's my analysis based on the images..."
    
    response = MultimodalChatResponse(
        response=response_text,
        model=request.model,
        images_processed=images_count
    )
    
    return DataResponse(
        code=200,
        message="Multimodal chat successful",
        data=response.dict()
    )


@router.get("/models", response_model=DataResponse)
async def get_available_models():
    """
    Get list of available AI models
    
    No authentication required
    """
    models = {
        "text": [
            {"id": "gpt-4", "name": "GPT-4", "provider": "OpenAI"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "provider": "OpenAI"},
            {"id": "claude-3", "name": "Claude 3", "provider": "Anthropic"},
            {"id": "gemini-pro", "name": "Gemini Pro", "provider": "Google"}
        ],
        "vision": [
            {"id": "gpt-4-vision", "name": "GPT-4 Vision", "provider": "OpenAI"},
            {"id": "gemini-pro-vision", "name": "Gemini Pro Vision", "provider": "Google"}
        ]
    }
    
    return DataResponse(
        code=200,
        message="Available models",
        data=models
    )


@router.delete("/history/{conversation_id}")
async def clear_conversation_history(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Clear conversation history
    
    - **conversation_id**: Conversation ID to clear
    """
    # In production, delete from database
    return DataResponse(
        code=200,
        message=f"Conversation {conversation_id} history cleared",
        data={"conversation_id": conversation_id}
    )
