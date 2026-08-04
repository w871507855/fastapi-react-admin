from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PermissionBrief(BaseModel):
    id: int
    name: str
    code: str
    type: int

    model_config = {"from_attributes": True}


class RoleOut(BaseModel):
    id: int
    code: str
    name: str
    description: str
    status: bool
    created_at: datetime
    permission_ids: list[int] = []

    model_config = {"from_attributes": True}


class RoleCreate(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=1, max_length=50)
    description: str = Field(default="", max_length=500)
    status: bool = True
    permission_ids: list[int] = []


class RoleUpdate(BaseModel):
    code: Optional[str] = Field(default=None, min_length=2, max_length=50)
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = Field(default=None, max_length=500)
    status: Optional[bool] = None
    permission_ids: Optional[list[int]] = None
