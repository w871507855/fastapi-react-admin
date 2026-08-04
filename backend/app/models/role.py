from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.associations import role_permissions, user_roles
from app.models.base import TimestampMixin


class Role(TimestampMixin, Base):
    __tablename__ = "roles"
    __table_args__ = {"comment": "角色表"}

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, comment="角色编码")
    name: Mapped[str] = mapped_column(String(50), comment="角色名称")
    description: Mapped[str] = mapped_column(Text, default="", comment="描述")
    status: Mapped[bool] = mapped_column(Boolean, default=True, comment="状态 1启用 0禁用")

    users: Mapped[list["User"]] = relationship(
        secondary=user_roles, back_populates="roles"
    )
    permissions: Mapped[list["Permission"]] = relationship(
        secondary=role_permissions, back_populates="roles", lazy="selectin"
    )
