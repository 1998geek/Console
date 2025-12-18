from datetime import datetime, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    混合验证逻辑:
    1. 先检查是否是明文匹配 (兼容 'admin123456' 这种遗留数据)
    2. 如果不是明文，再尝试 bcrypt 哈希验证
    """
    # Case A: 明文直接匹配 (处理遗留明文密码)
    if plain_password == hashed_password:
        return True
    
    # Case B: 尝试哈希验证
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # 如果 hashed_password 不是有效的哈希格式，verify 可能会抛错
        return False

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(subject: Union[str, Any], expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
