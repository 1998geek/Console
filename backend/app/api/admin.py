from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User as UserModel
from app.schemas.user import UserOut

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
