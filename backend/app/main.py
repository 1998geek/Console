from contextlib import asynccontextmanager
import time
from fastapi import FastAPI
from sqlalchemy import text
from app.api import auth, doc_tools, contract, agent, admin, multimodal, automation, tasks
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models import user

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Retry DB connection logic to handle race condition in docker-compose
    max_retries = 15
    retry_interval = 2
    
    for i in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database connection established.")
            break
        except Exception as e:
            if i == max_retries - 1:
                print(f"Could not connect to database after {max_retries} retries.")
                raise e
            print(f"Database not ready, retrying in {retry_interval}s... ({i+1}/{max_retries})")
            time.sleep(retry_interval)

    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="AI Console 接口文档",  # 修改这里
    description="企业级 AI 聚合平台后端 API，提供文档翻译、合同审查、智能体对话等服务。", # 增加中文描述
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    # 增加 Swagger UI 配置，使其更易读
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1, # 隐藏底部的 Schemas 模型，让界面更清爽
        "displayRequestDuration": True,
    }
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(doc_tools.router, prefix="/api/doc-tools", tags=["Document Tools"])
app.include_router(contract.router, prefix="/api/contract", tags=["Contract"])
app.include_router(agent.router, prefix="/api/agent", tags=["Agent"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(multimodal.router, prefix="/api/multimodal", tags=["Multimodal"])
app.include_router(automation.router, prefix="/api/automation", tags=["Automation"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])


@app.get("/")
def read_root():
    return {"message": "Welcome to AI Console Backend"}
