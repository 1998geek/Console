from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from app.api import deps
from app.services.azure_ai import AzureLLMService
from app.services.media_gen import SoraService
from app.db.redis_client import redis_conn

router = APIRouter(dependencies=[Depends(deps.get_current_user)])

@router.post("/vision/analyze")
async def analyze_vision(
    file: UploadFile = File(...),
    prompt: str = Form("请描述这张图片"),
    model: str | None = Form(None)
):
    try:
        content = await file.read()
        service = AzureLLMService()
        description = service.analyze_image(content, prompt)
        return {"description": description}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sora/generate")
async def sora_generate(
    prompt: str = Form(...),
    width: int = Form(...),
    height: int = Form(...),
    duration: int = Form(...),
    background_tasks: BackgroundTasks = None,
):
    task_id = SoraService.init_task(prompt, width=width, height=height, duration=duration)
    if background_tasks is not None:
        background_tasks.add_task(SoraService.mock_sora_generation, task_id, prompt, width, height, duration)
    else:
        SoraService.mock_sora_generation(task_id, prompt, width, height, duration)
    return {"task_id": task_id}

@router.get("/sora/status/{task_id}")
def sora_status(task_id: str):
    data = redis_conn.hgetall(f"task:{task_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "status": data.get("status"),
        "result": data.get("result"),
        "prompt": data.get("prompt"),
        "width": data.get("width"),
        "height": data.get("height"),
        "duration": data.get("duration"),
    }
