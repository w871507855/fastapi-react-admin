from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_permission
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.schemas.common import success
from app.schemas.role import RoleCreate, RoleOut, RoleUpdate

router = APIRouter(prefix="/roles", tags=["角色管理"])


def _apply_permissions(db: Session, role: Role, permission_ids: list[int] | None) -> None:
    if permission_ids is None:
        return
    role.permissions = (
        db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
        if permission_ids
        else []
    )


def _role_out(role: Role) -> dict:
    data = RoleOut.model_validate(role).model_dump()
    data["permission_ids"] = [p.id for p in role.permissions]
    return data


@router.get("")
def list_roles(
    page: int = 1,
    page_size: int = 10,
    keyword: str = "",
    status: bool | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("system:role:list")),
):
    query = db.query(Role)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(Role.name.like(like) | Role.code.like(like))
    if status is not None:
        query = query.filter(Role.status == status)
    total = query.count()
    items = query.order_by(Role.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return success({"total": total, "items": [_role_out(r) for r in items]})


@router.post("")
def create_role(
    data: RoleCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("system:role:add")),
):
    if db.query(Role).filter(Role.code == data.code).first():
        raise HTTPException(status_code=400, detail="角色编码已存在")
    role = Role(
        code=data.code,
        name=data.name,
        description=data.description,
        status=data.status,
    )
    _apply_permissions(db, role, data.permission_ids)
    db.add(role)
    db.commit()
    db.refresh(role)
    return success(_role_out(role))


@router.put("/{role_id}")
def update_role(
    role_id: int,
    data: RoleUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("system:role:update")),
):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    fields = data.model_dump(exclude_unset=True, exclude={"permission_ids"})
    if "code" in fields and fields["code"] != role.code:
        if db.query(Role).filter(Role.code == fields["code"]).first():
            raise HTTPException(status_code=400, detail="角色编码已存在")
    for key, value in fields.items():
        setattr(role, key, value)
    if "permission_ids" in data.model_dump(exclude_unset=True):
        _apply_permissions(db, role, data.permission_ids)
    db.commit()
    db.refresh(role)
    return success(_role_out(role))


@router.delete("/{role_id}")
def delete_role(
    role_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("system:role:delete")),
):
    role = db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    if role.users:
        raise HTTPException(status_code=400, detail="该角色下存在用户，无法删除")
    db.delete(role)
    db.commit()
    return success()
