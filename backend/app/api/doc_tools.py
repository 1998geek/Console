from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.services.translator import TranslationService
from app.schemas.business import TranslationMode, TextTranslationRequest, TextTranslationResponse
from app.services.azure_ai import AzureLLMService
from app.api import deps
from app.models.user import User
from urllib.parse import quote
import io

router = APIRouter(dependencies=[Depends(deps.get_current_user)])

# Instantiate services
translator_service = TranslationService()

@router.post("/translate/document")
async def translate_document(
    file: UploadFile = File(...),
    target_lang: str = Form(...),
    mode: TranslationMode = Form(TranslationMode.LOCAL)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
        
    ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    # Validation logic
    supported_extensions = ['docx', 'xlsx', 'pptx', 'pdf']
    if ext not in supported_extensions:
         raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Supported types: {', '.join(supported_extensions)}")
         
    if mode == TranslationMode.LOCAL and ext == 'pdf':
         raise HTTPException(status_code=400, detail="Local translation (LLM) does not support PDF yet. Please use Cloud mode.")

    content = await file.read()
    
    try:
        if mode == TranslationMode.CLOUD:
            result_stream = await translator_service.translate_by_cloud(content, file.filename, target_lang)
        else:
            result_stream = await translator_service.translate_by_llm(content, file.filename, target_lang)
            
        # Reset stream position just in case
        result_stream.seek(0)
        output_filename = f"translated_{file.filename}"
        encoded_filename = quote(output_filename)
        headers = {"Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}"}
        return StreamingResponse(result_stream, media_type="application/octet-stream", headers=headers)
    except Exception as e:
        # Log the full error in a real app
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/translate/text", response_model=TextTranslationResponse)
async def translate_text(request: TextTranslationRequest):
    try:
        llm_service = AzureLLMService()
        
        system_prompt = f"You are a professional translator. Translate the following text to {request.target_lang}."
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.text}
        ]
        
        # Call LLM
        response = llm_service.get_chat_completion(messages, model="gpt-4.1-mini", stream=False)
        
        translated_text = ""
        # Handle different response types (SDK vs REST)
        if hasattr(response, 'choices'): # OpenAI SDK Response
            translated_text = response.choices[0].message.content.strip()
        elif hasattr(response, 'json'): # Requests Response (REST)
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                translated_text = data['choices'][0]['message']['content'].strip()
        else:
             raise Exception("Unknown response format from LLM service")
                 
        return TextTranslationResponse(
            original_text=request.text,
            translated_text=translated_text,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
