from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, alias_generators


class _Base(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
    )


class ClusterSummary(_Base):
    id: int | None = None
    name: str = ""
    kind: str | None = None
    version: str | None = None
    status: str | None = None
    master_ip: str | None = None
    master_port: int | None = None


class ClusterDetail(ClusterSummary):
    node_count: int | None = None


class ClusterNode(_Base):
    id: int | None = None
    name: str = ""
    ip: str = ""
    status: str | None = None
    roles: list[str] = Field(default_factory=list)


class ClusterPartition(_Base):
    id: int | None = None
    name: str = ""
    cluster_id: int | None = None


class PartitionResource(_Base):
    host_ids: str = ""
    cpu_total: float | None = None
    cpu_used: float | None = None
    mem_total: float | None = None
    mem_used: float | None = None
