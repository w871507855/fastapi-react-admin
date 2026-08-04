from typing import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import SessionLocal
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str | None = Depends(oauth2_scheme)
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="未登录或登录已过期"
        )
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的凭证"
        )
    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在"
        )
    if not user.status:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁用"
        )
    return user


def _build_permission_set(user: User) -> set[str]:
    codes: set[str] = set()
    for role in user.roles:
        for perm in role.permissions:
            if perm.code:
                codes.add(perm.code)
    return codes


def require_permission(code: str) -> Callable:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser:
            return current_user
        if code not in _build_permission_set(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"没有权限: {code}"
            )
        return current_user

    return dependency
