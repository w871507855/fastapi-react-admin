from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class UserBrief(BaseModel):
    id: int
    username: str
    nickname: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserBrief
