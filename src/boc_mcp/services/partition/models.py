from __future__ import annotations

from pydantic import BaseModel, ConfigDict, alias_generators


class _Base(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
    )


class Partition(_Base):
    id: int | None = None
    name: str = ""


class PartitionNode(_Base):
    id: int | None = None
    name: str = ""
    ip: str = ""


class HostNode(_Base):
    id: int | None = None
    name: str = ""
    ip: str = ""
