"""
Security utilities: JWT token, password hashing, etc.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token scheme for Swagger UI
# scheme_name must match the security scheme in OpenAPI docs
security = HTTPBearer(
    auto_error=True,
    scheme_name="Bearer",
    description="JWT Authentication - Enter your access token from /auth/login"
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current user from JWT token"""
    try:
        print(f"🔍 DEBUG: get_current_user called")
        print(f"🔍 DEBUG: Received credentials object: {credentials}")
        print(f"🔍 DEBUG: Credentials type: {type(credentials)}")
        
        if credentials is None:
            print(f"❌ DEBUG: Credentials is None!")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No credentials provided",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        token = credentials.credentials
        print(f"🔍 DEBUG: Extracted token (first 30 chars): {token[:30]}..." if len(token) > 30 else f"🔍 DEBUG: Extracted token: {token}")
        
        payload = decode_token(token)
        print(f"🔍 DEBUG: Decoded payload: {payload}")
        
        if payload.get("type") != "access":
            print(f"❌ DEBUG: Invalid token type: {payload.get('type')}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        username: str = payload.get("sub")
        if username is None:
            print(f"❌ DEBUG: No username in payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        print(f"✅ DEBUG: Authentication successful for user: {username}")
        return {
            "username": username,
            "is_admin": payload.get("is_admin", False)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ DEBUG: Unexpected error in get_current_user: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Verify current user is an admin"""
    if not current_user.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
