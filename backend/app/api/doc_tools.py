from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import StreamingResponse
from app.services.translator import TranslationService
from app.schemas.business import TranslationMode, TextTranslationRequest, TextTranslationResponse
from app.services.azure_ai import AzureLLMService
from app.api import deps
from app.models.user import User
from urllib.parse import quote
import io
from io import BytesIO
try:
    from docx import Document
except ImportError:
    Document = None

from app.utils.docx_numbering import DocxNumberingService

router = APIRouter(dependencies=[Depends(deps.get_current_user)])

# Instantiate services
translator_service = TranslationService()
docx_numbering_service = DocxNumberingService()

@router.post(
    "/translate/document/task",
    summary="文档翻译 (异步任务)",
    description="上传文件并启动异步翻译任务，返回 task_id。支持进度查询。"
)
async def translate_document_task(
    file: UploadFile = File(..., description="待翻译的文件"),
    target_lang: str = Form(..., description="目标语言代码 (如 zh-Hans, en)"),
    mode: TranslationMode = Form(TranslationMode.LOCAL, description="翻译模式: cloud 或 local"),
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
            task_id = await translator_service.start_cloud_translation_task(content, file.filename, target_lang)
            return {"task_id": task_id, "message": "Translation task started"}
        else:
            # Placeholder for Local LLM async implementation
            raise HTTPException(status_code=501, detail="Async mode for Local translation is coming soon. Please use Sync mode or Cloud Async.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start translation task: {str(e)}")


@router.post(
    "/translate/document",
    summary="文档翻译 (上传文件)",  # ✅ 接口显示的中文名
    description="支持上传 .docx, .pdf, .pptx 等文件。Cloud 模式支持格式保留，Local 模式支持语义优化。" # ✅ 详细描述
)
async def translate_document(
    file: UploadFile = File(..., description="待翻译的文件"),
    target_lang: str = Form(..., description="目标语言代码 (如 zh-Hans, en)"),
    mode: TranslationMode = Form(TranslationMode.LOCAL, description="翻译模式: cloud 或 local"),
    translate_sheet_names: str | None = Form(None)
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
            tsn = False
            if translate_sheet_names is not None:
                tsn = translate_sheet_names.lower() == "true"
            result_stream = await translator_service.translate_by_llm(content, file.filename, target_lang, translate_sheet_names=tsn)
            
        # Reset stream position just in case
        result_stream.seek(0)
        output_filename = f"translated_{file.filename}"
        encoded_filename = quote(output_filename)
        headers = {"Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}"}
        return StreamingResponse(result_stream, media_type="application/octet-stream", headers=headers)
    except Exception as e:
        # Log the full error in a real app
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post(
    "/translate/text",
    summary="纯文本翻译", # ✅
    response_model=TextTranslationResponse
)
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

@router.post("/numbering")
async def numbering_docx(
    file: UploadFile = File(...),
):
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx is supported for numbering")
    
    content = await file.read()
    try:
        output_stream = docx_numbering_service.process(BytesIO(content))
        
        encoded_filename = quote(f"numbered_{file.filename}")
        headers = {"Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}"}
        return StreamingResponse(output_stream, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers=headers)
    except ImportError:
         raise HTTPException(status_code=500, detail="python-docx not installed on server")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Numbering failed: {str(e)}")
