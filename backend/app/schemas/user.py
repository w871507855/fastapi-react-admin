from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RoleBrief(BaseModel):
    id: int
    code: str
    name: str

    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    id: int
    username: str
    nickname: str
    email: str
    phone: str
    status: bool
    is_superuser: bool
    created_at: datetime
    roles: list[RoleBrief] = []

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    nickname: str = Field(default="", max_length=50)
    password: str = Field(min_length=6, max_length=128)
    email: str = Field(default="", max_length=100)
    phone: str = Field(default="", max_length=20)
    status: bool = True
    role_ids: list[int] = []


class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(default=None, max_length=50)
    email: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    status: Optional[bool] = None
    role_ids: Optional[list[int]] = None


class UserStatusUpdate(BaseModel):
    status: bool


class PasswordUpdate(BaseModel):
    password: str = Field(min_length=6, max_length=128)
