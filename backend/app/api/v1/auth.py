from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import create_access_token
from app.core.config import settings
from app.services.db_service import DatabaseManager
from datetime import timedelta

router = APIRouter()
db_manager = DatabaseManager()

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password # 获取原始密码
    
    # 1. 超级管理员后门
    if username == "admin" and password == "admin123456":
        access_token = create_access_token(
            data={"sub": username, "is_admin": True},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": access_token, "token_type": "bearer"}

    # 2. 数据库验证 (传入原始密码，由内部判断是明文还是哈希)
    if not db_manager.verify_user(username, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. 生成 Token
    access_token = create_access_token(
        data={"sub": username, "is_admin": False},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
