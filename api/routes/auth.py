"""
Authentication Routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from ..models.request import LoginRequest, RefreshTokenRequest
from ..models.response import TokenResponse, UserInfo, DataResponse
from ..core.security import (
    verify_password, 
    create_access_token, 
    create_refresh_token,
    decode_token,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Mock user database - In production, use a real database
USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": "$2b$12$LQvZ9d0KKr5l5HxH5Y5Y5OU5X5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5O",  # password: admin123
        "is_admin": True
    },
    "user": {
        "username": "user",
        "hashed_password": "$2b$12$LQvZ9d0KKr5l5HxH5Y5Y5OU5X5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5Y5O",  # password: user123
        "is_admin": False
    }
}


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    User login endpoint
    
    Demo credentials:
    - admin / admin123 (admin user)
    - user / user123 (regular user)
    """
    user = USERS_DB.get(request.username)
    
    # For demo purposes, accept simple passwords
    # In production, use proper password hashing
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Simple password check for demo
    if not (request.password == "admin123" and request.username == "admin") and \
       not (request.password == "user123" and request.username == "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create tokens
    token_data = {
        "sub": user["username"],
        "is_admin": user["is_admin"]
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=86400
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    try:
        payload = decode_token(request.refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Create new access token
        token_data = {
            "sub": payload.get("sub"),
            "is_admin": payload.get("is_admin", False)
        }
        
        access_token = create_access_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=request.refresh_token,  # Return same refresh token
            token_type="bearer",
            expires_in=86400
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@router.get("/me", response_model=DataResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current user information
    """
    user_info = UserInfo(
        username=current_user["username"],
        is_admin=current_user["is_admin"]
    )
    
    return DataResponse(
        code=200,
        message="success",
        data=user_info.dict()
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    User logout endpoint
    
    Note: JWT tokens are stateless. In production, implement token blacklisting
    or use Redis to track invalidated tokens.
    """
    return DataResponse(
        code=200,
        message="Logged out successfully",
        data={"username": current_user["username"]}
    )
