from typing import Optional

from pydantic import BaseModel, Field


class PermissionOut(BaseModel):
    id: int
    parent_id: int
    name: str
    code: str
    type: int
    path: str
    component: str
    icon: str
    sort: int
    status: bool
    children: list["PermissionOut"] = []

    model_config = {"from_attributes": True}


class PermissionCreate(BaseModel):
    parent_id: int = 0
    name: str = Field(min_length=1, max_length=50)
    code: str = Field(default="", max_length=100)
    type: int = Field(default=2, ge=1, le=3)
    path: str = Field(default="", max_length=200)
    component: str = Field(default="", max_length=200)
    icon: str = Field(default="", max_length=50)
    sort: int = 0
    status: bool = True


class PermissionUpdate(BaseModel):
    parent_id: Optional[int] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    code: Optional[str] = Field(default=None, max_length=100)
    type: Optional[int] = Field(default=None, ge=1, le=3)
    path: Optional[str] = Field(default=None, max_length=200)
    component: Optional[str] = Field(default=None, max_length=200)
    icon: Optional[str] = Field(default=None, max_length=50)
    sort: Optional[int] = None
    status: Optional[bool] = None


PermissionOut.model_rebuild()
