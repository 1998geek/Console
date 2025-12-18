from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from app.api import deps
from app.services.azure_ai import AzureLLMService
from app.services.media_gen import SoraService
from app.db.redis_client import redis_conn

router = APIRouter(dependencies=[Depends(deps.get_current_user)])

@router.post("/vision/analyze")
async def analyze_vision(file: UploadFile = File(...), prompt: str = Form("请描述这张图片")):
    try:
        content = await file.read()
        service = AzureLLMService()
        description = service.analyze_image(content, prompt)
        return {"description": description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sora/generate")
async def sora_generate(prompt: str = Form(...), background_tasks: BackgroundTasks = None):
    task_id = SoraService.init_task(prompt)
    if background_tasks is not None:
        background_tasks.add_task(SoraService.mock_sora_generation, task_id, prompt)
    else:
        SoraService.mock_sora_generation(task_id, prompt)
    return {"task_id": task_id}

@router.get("/sora/status/{task_id}")
def sora_status(task_id: str):
    data = redis_conn.hgetall(f"task:{task_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": data.get("status"), "result": data.get("result")}
