from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.associations import role_permissions
from app.models.base import TimestampMixin


class Permission(TimestampMixin, Base):
    __tablename__ = "permissions"
    __table_args__ = {"comment": "权限/菜单表"}

    # 类型常量
    TYPE_DIRECTORY = 1
    TYPE_MENU = 2
    TYPE_BUTTON = 3

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    parent_id: Mapped[int] = mapped_column(
        Integer, default=0, index=True, comment="父级ID，0为根"
    )
    name: Mapped[str] = mapped_column(String(50), comment="名称")
    code: Mapped[str] = mapped_column(String(100), default="", comment="权限编码")
    type: Mapped[int] = mapped_column(Integer, default=TYPE_MENU, comment="1目录 2菜单 3按钮")
    path: Mapped[str] = mapped_column(String(200), default="", comment="前端路由")
    component: Mapped[str] = mapped_column(String(200), default="", comment="前端组件")
    icon: Mapped[str] = mapped_column(String(50), default="", comment="图标")
    sort: Mapped[int] = mapped_column(Integer, default=0, comment="排序")
    status: Mapped[bool] = mapped_column(Boolean, default=True, comment="状态 1启用 0禁用")

    roles: Mapped[list["Role"]] = relationship(
        secondary=role_permissions, back_populates="permissions"
    )
