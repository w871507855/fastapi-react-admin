from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.rbac import get_user_menu_tree, get_user_permission_codes
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, UserBrief
from app.schemas.common import success

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    if not user.status:
        raise HTTPException(status_code=400, detail="账号已被禁用")
    token = create_access_token(user.id)
    return success(
        LoginResponse(
            access_token=token,
            user=UserBrief(id=user.id, username=user.username, nickname=user.nickname),
        ).model_dump()
    )


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    data = {
        "id": current_user.id,
        "username": current_user.username,
        "nickname": current_user.nickname,
        "email": current_user.email,
        "phone": current_user.phone,
        "is_superuser": current_user.is_superuser,
        "roles": [r.name for r in current_user.roles],
        "permissions": sorted(get_user_permission_codes(current_user)),
    }
    return success(data)


@router.get("/menus")
def menus(current_user: User = Depends(get_current_user)):
    return success(get_user_menu_tree(current_user))
