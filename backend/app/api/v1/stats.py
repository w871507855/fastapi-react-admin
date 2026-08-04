from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.schemas.common import success

router = APIRouter(prefix="/stats", tags=["统计"])


@router.get("")
def stats(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return success(
        {
            "users": db.query(User).count(),
            "roles": db.query(Role).count(),
            "permissions": db.query(Permission).count(),
        }
    )
