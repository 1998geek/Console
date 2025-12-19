from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from app.core.config import settings
from app.api.v1 import auth, translate  # 引入新路由
from pathlib import Path

app = FastAPI(title=settings.PROJECT_NAME)

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(translate.router, prefix="/api/v1/translate", tags=["translation"]) # 注册翻译路由

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Portal Backend API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/download/{filename}")
async def download_file(filename: str):
    safe_name = Path(filename).name
    file_path = UPLOAD_DIR / safe_name
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path), filename=safe_name)
    raise HTTPException(status_code=404, detail="文件不存在")
