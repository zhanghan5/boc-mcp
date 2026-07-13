from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ServiceTreeNode(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        alias_generator=lambda s: s,
        populate_by_name=True,
    )

    has_children: bool | None = None
    id: int | None = None
    name: str = ""
    pid: int | None = None
    ptype: str | None = None
    type: str | None = None
