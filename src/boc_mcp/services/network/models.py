from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class NetworkPartition(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: int | None = None
    name: str = ""
