from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.associations import user_roles
from app.models.base import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "用户表"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment="用户名")
    nickname: Mapped[str] = mapped_column(String(50), default="", comment="昵称")
    password_hash: Mapped[str] = mapped_column(String(128), comment="密码哈希")
    email: Mapped[str] = mapped_column(String(100), default="", comment="邮箱")
    phone: Mapped[str] = mapped_column(String(20), default="", comment="手机号")
    status: Mapped[bool] = mapped_column(Boolean, default=True, comment="状态 1启用 0禁用")
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否超级管理员")

    roles: Mapped[list["Role"]] = relationship(
        secondary=user_roles, back_populates="users", lazy="selectin"
    )
