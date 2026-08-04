from sqlalchemy import Table, Column, ForeignKey

from app.db.session import Base

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    comment="用户-角色关联表",
)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "permission_id", ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True
    ),
    comment="角色-权限关联表",
)
