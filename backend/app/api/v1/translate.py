from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from app.services.blob_service import AzureBlobService
from app.services.translator_service import AzureDocumentTranslator, background_track_translation
from utils.redis_client import redis_client
import uuid

router = APIRouter()

# 实例化服务 (在 FastAPI 中也可以用 Depends 注入，这里简单起见直接实例化)
blob_service = AzureBlobService()
translator = AzureDocumentTranslator()

@router.post("/upload")
async def upload_and_translate(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = Form(...)
):
    """
    异步翻译接口：
    1. 接收文件并上传到 Azure Blob
    2. 提交翻译任务给 Azure
    3. 启动后台线程轮询状态
    4. 立即返回 task_id 给前端
    """
    try:
        # 1. 生成唯一任务 ID
        task_id = str(uuid.uuid4())
        
        # 2. 读取文件内容
        file_content = await file.read()
        
        # 3. 上传到 Azure Blob (返回 Blob 路径)
        # 初始状态写入 Redis
        redis_client.set_task_progress(task_id, 1, "正在上传文件到云端...", "processing")
        
        blob_name = blob_service.upload_file(file_content, file.filename)
        
        # 4. 提交翻译任务 (获取 Poller 对象，不等待结果)
        redis_client.set_task_progress(task_id, 5, "正在提交翻译请求...", "processing")
        poller = translator.start_translation_job(blob_name, to_language=language)
        
        # 5. 添加后台任务 (这是 FastAPI 的魔法，请求返回后，这个函数会在后台继续跑)
        background_tasks.add_task(
            background_track_translation, 
            task_id, 
            blob_name, 
            translator, 
            poller
        )
        
        return {"task_id": task_id, "message": "Translation started"}

    except Exception as e:
        # 如果启动阶段就挂了，记录错误
        print(f"Error starting translation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}")
async def get_translation_status(task_id: str):
    """
    查询任务进度 (前端轮询用)
    """
    progress_data = redis_client.get_task_progress(task_id)
    if not progress_data:
        raise HTTPException(status_code=404, detail="Task not found")
    return progress_data
