from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _Base(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class VersionSummary(_Base):
    id: int | None = None
    name: str = ""


class ImageGroup(_Base):
    id: int | None = None
    name: str = ""
