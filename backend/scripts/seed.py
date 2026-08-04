"""初始化数据库基础数据：管理员、角色、权限菜单。

用法（在 backend 目录下执行）：
    python -m scripts.seed
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app.core.config import load_dotenv_if_exists

load_dotenv_if_exists()

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"
ADMIN_NICKNAME = "超级管理员"

# 权限结构：(name, code, type, path, component, icon, sort, children)
MENU_STRUCTURE = [
    {
        "name": "首页",
        "code": "",
        "type": Permission.TYPE_MENU,
        "path": "/dashboard",
        "component": "dashboard",
        "icon": "DashboardOutlined",
        "sort": 1,
        "children": [],
    },
    {
        "name": "系统管理",
        "code": "",
        "type": Permission.TYPE_DIRECTORY,
        "path": "/system",
        "component": "",
        "icon": "SettingOutlined",
        "sort": 2,
        "children": [
            {
                "name": "用户管理",
                "code": "",
                "type": Permission.TYPE_MENU,
                "path": "/system/user",
                "component": "system/user",
                "icon": "UserOutlined",
                "sort": 1,
                "children": [
                    ("用户查询", "system:user:list"),
                    ("新增用户", "system:user:add"),
                    ("修改用户", "system:user:update"),
                    ("删除用户", "system:user:delete"),
                ],
            },
            {
                "name": "角色管理",
                "code": "",
                "type": Permission.TYPE_MENU,
                "path": "/system/role",
                "component": "system/role",
                "icon": "TeamOutlined",
                "sort": 2,
                "children": [
                    ("角色查询", "system:role:list"),
                    ("新增角色", "system:role:add"),
                    ("修改角色", "system:role:update"),
                    ("删除角色", "system:role:delete"),
                ],
            },
            {
                "name": "权限管理",
                "code": "",
                "type": Permission.TYPE_MENU,
                "path": "/system/permission",
                "component": "system/permission",
                "icon": "SafetyOutlined",
                "sort": 3,
                "children": [
                    ("权限查询", "system:permission:list"),
                    ("新增权限", "system:permission:add"),
                    ("修改权限", "system:permission:update"),
                    ("删除权限", "system:permission:delete"),
                ],
            },
        ],
    },
]


def _create_permissions(db, node, parent_id=0):
    children = node.get("children", [])
    perm = Permission(
        parent_id=parent_id,
        name=node["name"],
        code=node.get("code", ""),
        type=node["type"],
        path=node.get("path", ""),
        component=node.get("component", ""),
        icon=node.get("icon", ""),
        sort=node.get("sort", 0),
        status=True,
    )
    db.add(perm)
    db.flush()
    for child in children:
        if isinstance(child, tuple):
            name, code = child
            db.add(
                Permission(
                    parent_id=perm.id,
                    name=name,
                    code=code,
                    type=Permission.TYPE_BUTTON,
                    sort=0,
                    status=True,
                )
            )
        else:
            _create_permissions(db, child, perm.id)
    return perm


def main():
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username == ADMIN_USERNAME).first():
            print(f"[跳过] 用户 {ADMIN_USERNAME} 已存在")
        else:
            admin = User(
                username=ADMIN_USERNAME,
                nickname=ADMIN_NICKNAME,
                password_hash=hash_password(ADMIN_PASSWORD),
                status=True,
                is_superuser=True,
            )
            db.add(admin)
            print(f"[创建] 超级管理员 {ADMIN_USERNAME}/{ADMIN_PASSWORD}")

        if db.query(Permission).count() == 0:
            for node in MENU_STRUCTURE:
                _create_permissions(db, node)
            print("[创建] 权限菜单结构")
        else:
            print("[跳过] 权限菜单已存在")

        admin_role = db.query(Role).filter(Role.code == "admin").first()
        if not admin_role:
            admin_role = Role(
                code="admin",
                name="管理员",
                description="拥有系统全部权限",
                status=True,
            )
            all_perms = db.query(Permission).all()
            admin_role.permissions = all_perms
            db.add(admin_role)
            print("[创建] 管理员角色")

        common_role = db.query(Role).filter(Role.code == "common").first()
        if not common_role:
            common_role = Role(
                code="common",
                name="普通用户",
                description="只读基础权限",
                status=True,
            )
            list_perms = (
                db.query(Permission)
                .filter(
                    Permission.code.in_(
                        ["system:user:list", "system:role:list", "system:permission:list"]
                    )
                )
                .all()
            )
            common_role.permissions = list_perms
            db.add(common_role)
            print("[创建] 普通用户角色")

        db.commit()
        print("初始化完成")
    finally:
        db.close()


if __name__ == "__main__":
    main()
