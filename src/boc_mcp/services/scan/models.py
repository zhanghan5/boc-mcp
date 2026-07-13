from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class ScanStrategy(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: int | None = None
    name: str = ""


class ScanReport(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: int | None = None
    name: str = ""
