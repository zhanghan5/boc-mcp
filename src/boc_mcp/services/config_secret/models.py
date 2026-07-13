from __future__ import annotations

from pydantic import BaseModel, ConfigDict, alias_generators


class _Base(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
    )


class SecretItem(_Base):
    name: str = ""
    namespace: str = ""
    type: str | None = None
