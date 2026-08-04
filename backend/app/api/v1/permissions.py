from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_permission
from app.core.rbac import build_menu_tree
from app.models.permission import Permission
from app.models.user import User
from app.schemas.common import success
from app.schemas.permission import PermissionCreate, PermissionUpdate

router = APIRouter(prefix="/permissions", tags=["权限管理"])


@router.get("/tree")
def get_tree(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("system:permission:list")),
):
    perms = db.query(Permission).order_by(Permission.sort, Permission.id).all()
    return success(build_menu_tree(perms))


@router.get("")
def get_all(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("system:permission:list")),
):
    perms = db.query(Permission).order_by(Permission.sort, Permission.id).all()
    return success([_to_flat(p) for p in perms])


def _to_flat(perm: Permission) -> dict:
    return {
        "id": perm.id,
        "parent_id": perm.parent_id,
        "name": perm.name,
        "code": perm.code,
        "type": perm.type,
        "path": perm.path,
        "component": perm.component,
        "icon": perm.icon,
        "sort": perm.sort,
        "status": perm.status,
    }


@router.post("")
def create_permission(
    data: PermissionCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("system:permission:add")),
):
    if data.parent_id:
        parent = db.get(Permission, data.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="父级权限不存在")
        if data.type == Permission.TYPE_DIRECTORY:
            raise HTTPException(status_code=400, detail="目录只能作为顶级节点")
    perm = Permission(**data.model_dump())
    db.add(perm)
    db.commit()
    db.refresh(perm)
    return success(_to_flat(perm))


@router.put("/{permission_id}")
def update_permission(
    permission_id: int,
    data: PermissionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("system:permission:update")),
):
    perm = db.get(Permission, permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="权限不存在")
    fields = data.model_dump(exclude_unset=True)
    new_parent = fields.get("parent_id", perm.parent_id)
    if new_parent == perm.id:
        raise HTTPException(status_code=400, detail="父级不能是自己")
    if new_parent and fields.get("type", perm.type) == Permission.TYPE_DIRECTORY:
        raise HTTPException(status_code=400, detail="目录只能作为顶级节点")
    for key, value in fields.items():
        setattr(perm, key, value)
    db.commit()
    db.refresh(perm)
    return success(_to_flat(perm))


@router.delete("/{permission_id}")
def delete_permission(
    permission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("system:permission:delete")),
):
    perm = db.get(Permission, permission_id)
    if not perm:
        raise HTTPException(status_code=404, detail="权限不存在")
    if db.query(Permission).filter(Permission.parent_id == permission_id).count():
        raise HTTPException(status_code=400, detail="存在子节点，请先删除子节点")
    db.delete(perm)
    db.commit()
    return success()
