import time
import uuid
from typing import Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint


def new_id() -> str:
    """Small helper so every row gets a readable unique string id."""
    return uuid.uuid4().hex


def now_ts() -> float:
    """Store timestamps as simple Unix seconds."""
    return time.time()


class Domain(SQLModel, table=True):
    __tablename__ = "domains"
    __table_args__ = (
        UniqueConstraint("user", "slug", name="uq_domain_user_slug"),
    )

    id: str = Field(default_factory=new_id, primary_key=True)
    user: str
    slug: str
    title: str
    dataset_name: str = Field(unique=True, index=True)
    created_at: float = Field(default_factory=now_ts)


class Session(SQLModel, table=True):
    __tablename__ = "sessions"

    id: str = Field(default_factory=new_id, primary_key=True)
    domain_id: str = Field(foreign_key="domains.id", index=True)
    query: str
    status: str = Field(default="planning", index=True)
    output: Optional[str] = None
    created_at: float = Field(default_factory=now_ts)
    completed_at: Optional[float] = None


class Source(SQLModel, table=True):
    __tablename__ = "sources"

    id: str = Field(default_factory=new_id, primary_key=True)
    domain_id: str = Field(foreign_key="domains.id", index=True)
    cognee_data_id: Optional[str] = Field(default=None, index=True)
    kind: str
    uri: str
    title: Optional[str] = None
    added_at: float = Field(default_factory=now_ts)


class Confidence(SQLModel, table=True):
    __tablename__ = "confidence"
    __table_args__ = (
        UniqueConstraint("domain_id", "node_ref", name="uq_confidence_domain_node"),
    )

    id: str = Field(default_factory=new_id, primary_key=True)
    domain_id: str = Field(foreign_key="domains.id", index=True)
    node_ref: str = Field(index=True)
    score: float = Field(default=0.5)
    upvotes: int = Field(default=0)
    last_seen: float = Field(default_factory=now_ts)
    forgotten: int = Field(default=0)