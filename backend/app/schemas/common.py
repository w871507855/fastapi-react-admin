from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PageResult(BaseModel, Generic[T]):
    total: int
    items: list[T]


def success(data: Any = None, message: str = "ok") -> dict:
    return {"code": 0, "message": message, "data": data}


def fail(message: str = "操作失败", code: int = 1, data: Any = None) -> dict:
    return {"code": code, "message": message, "data": data}
