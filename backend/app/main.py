from contextlib import asynccontextmanager
import time
from fastapi import FastAPI
from sqlalchemy import text
from app.api import auth, doc_tools
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
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(doc_tools.router, prefix="/api/doc-tools", tags=["Document Tools"])


@app.get("/")
def read_root():
    return {"message": "Welcome to AI Console Backend"}
