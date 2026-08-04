from app.models.permission import Permission
from app.models.user import User


def get_user_permission_codes(user: User) -> set[str]:
    codes: set[str] = set()
    for role in user.roles:
        for perm in role.permissions:
            if perm.code:
                codes.add(perm.code)
    return codes


def build_menu_tree(permissions: list[Permission]) -> list[dict]:
    nodes: dict[int, dict] = {}
    roots: list[dict] = []

    for perm in sorted(permissions, key=lambda p: (p.sort, p.id)):
        nodes[perm.id] = {
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
            "children": [],
        }

    for node in nodes.values():
        parent = nodes.get(node["parent_id"])
        if parent is not None:
            parent["children"].append(node)
        else:
            roots.append(node)
    return roots


def get_user_menu_tree(user: User) -> list[dict]:
    """超级管理员返回全部菜单，否则返回角色权限中类型为目录/菜单的节点。"""
    perms = _collect_menu_permissions(user)
    return build_menu_tree(perms)


def _collect_menu_permissions(user: User) -> list[Permission]:
    if user.is_superuser:
        return _all_menu_permissions()
    seen: dict[int, Permission] = {}
    for role in user.roles:
        for perm in role.permissions:
            if perm.type in (Permission.TYPE_DIRECTORY, Permission.TYPE_MENU):
                seen[perm.id] = perm
    return list(seen.values())


def _all_menu_permissions() -> list[Permission]:
    from sqlalchemy.orm import Session

    from app.db.session import SessionLocal

    db: Session = SessionLocal()
    try:
        return (
            db.query(Permission)
            .filter(
                Permission.type.in_(
                    [Permission.TYPE_DIRECTORY, Permission.TYPE_MENU]
                )
            )
            .all()
        )
    finally:
        db.close()
