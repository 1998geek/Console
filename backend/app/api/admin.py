from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User as UserModel
from app.schemas.user import UserOut, UserCreate
from app.core import security

router = APIRouter(dependencies=[Depends(deps.get_current_user)])

@router.get("/users", response_model=List[UserOut])
def list_users(
    current_user=Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    users = db.query(UserModel).all()
    return users

@router.post("/users")
def create_user(
    user_in: UserCreate,
    current_user=Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    existing = db.query(UserModel).filter(UserModel.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    hashed = security.get_password_hash(user_in.password)
    user = UserModel(username=user_in.username, email=user_in.email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"success": True, "id": user.id}

@router.post("/users/{username}/reset-password")
def reset_password(
    username: str,
    payload: dict,
    current_user=Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    new_password = payload.get("password")
    if not new_password:
        raise HTTPException(status_code=400, detail="缺少新密码")
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.hashed_password = security.get_password_hash(new_password)
    db.add(user)
    db.commit()
    return {"success": True}

@router.delete("/users/{username}")
def delete_user(
    username: str,
    current_user=Depends(deps.get_current_user),
    db: Session = Depends(deps.get_db)
):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
    if username == "admin":
        raise HTTPException(status_code=400, detail="禁止删除管理员账户")
    user = db.query(UserModel).filter(UserModel.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(user)
    db.commit()
    return {"success": True}
