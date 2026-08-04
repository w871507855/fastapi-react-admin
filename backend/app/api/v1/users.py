from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_permission
from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User
from app.schemas.common import PageResult, success
from app.schemas.user import (
    PasswordUpdate,
    UserCreate,
    UserOut,
    UserStatusUpdate,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("")
def list_users(
    page: int = 1,
    page_size: int = 10,
    keyword: str = "",
    status: bool | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("system:user:list")),
):
    query = db.query(User)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            User.username.like(like) | User.nickname.like(like) | User.phone.like(like)
        )
    if status is not None:
        query = query.filter(User.status == status)
    total = query.count()
    items = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success(PageResult[UserOut](total=total, items=items).model_dump())


@router.post("")
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("system:user:add")),
):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=data.username,
        nickname=data.nickname or data.username,
        password_hash=hash_password(data.password),
        email=data.email,
        phone=data.phone,
        status=data.status,
    )
    if data.role_ids:
        user.roles = db.query(Role).filter(Role.id.in_(data.role_ids)).all()
    db.add(user)
    db.commit()
    db.refresh(user)
    return success(UserOut.model_validate(user).model_dump())


@router.put("/{user_id}")
def update_user(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("system:user:update")),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    fields = data.model_dump(exclude_unset=True, exclude={"role_ids"})
    for key, value in fields.items():
        setattr(user, key, value)
    if "role_ids" in data.model_dump(exclude_unset=True):
        if data.role_ids is None:
            user.roles = []
        else:
            user.roles = db.query(Role).filter(Role.id.in_(data.role_ids)).all()
    db.commit()
    db.refresh(user)
    return success(UserOut.model_validate(user).model_dump())


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("system:user:delete")),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.is_superuser:
        raise HTTPException(status_code=400, detail="超级管理员不可删除")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")
    db.delete(user)
    db.commit()
    return success()


@router.put("/{user_id}/status")
def update_status(
    user_id: int,
    data: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("system:user:update")),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user.is_superuser and not data.status:
        raise HTTPException(status_code=400, detail="超级管理员不可禁用")
    if user.id == current_user.id and not data.status:
        raise HTTPException(status_code=400, detail="不能禁用自己")
    user.status = data.status
    db.commit()
    return success()


@router.put("/{user_id}/password")
def reset_password(
    user_id: int,
    data: PasswordUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("system:user:update")),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.password_hash = hash_password(data.password)
    db.commit()
    return success()
