from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class _Base(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class WorkloadSummary(_Base):
    id: int | None = None
    name: str = ""
    namespace: str | None = None
    status: str | None = None


class ContainerSummary(_Base):
    id: int | None = None
    name: str = ""
    image: str | None = None
    pod_name: str | None = None


class PodSummary(_Base):
    id: int | None = None
    name: str = ""
    namespace: str | None = None
    status: str | None = None
    node_ip: str | None = None


class ServiceSummary(_Base):
    id: int | None = None
    name: str = ""
    namespace: str | None = None
    cluster_ip: str | None = None
    svc_type: str | None = None
