from __future__ import annotations

from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ListResult(BaseModel, Generic[T]):
    items: list[T] = Field(default_factory=list)
    page: int = 1
    page_size: int = 20
    total: int = 0
    page_count: int = 0

    @classmethod
    def from_legacy(cls, payload: dict[str, Any], *, items_key: str = "rows") -> "ListResult[Any]":
        data = payload.get("data")
        if isinstance(data, dict) and items_key in data:
            source = data
        else:
            source = payload
        return cls(
            items=source.get(items_key) or [],
            page=source.get("currPageNum", 1),
            page_size=source.get("pageSize", 20),
            total=source.get("totalCount", 0),
            page_count=source.get("pageCount", 0),
        )


class ActionResult(BaseModel):
    success: bool = True
    message: str = ""
