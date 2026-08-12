import uuid
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class ProductLine(StrEnum):
    HOTEL = "hotel"
    FLIGHT = "flight"


class PoolStatus(StrEnum):
    SOURCING = "sourcing"
    SUBMITTED = "submitted"
    VALIDATING = "validating"
    READY_FOR_GRADING = "ready_for_grading"
    GRADING = "grading"
    PENDING_REVIEW = "pending_review"
    READY_TO_LIST = "ready_to_list"
    LISTED = "listed"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Campaign(TimestampMixin, Base):
    __tablename__ = "campaigns"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default="draft", index=True)
    target_markets: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    product_lines: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sourcing_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    owner_id: Mapped[str | None] = mapped_column(String(100))
    requirements: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)


class SourcingTask(TimestampMixin, Base):
    __tablename__ = "sourcing_tasks"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campaigns.id"), index=True)
    product_line: Mapped[ProductLine] = mapped_column(Enum(ProductLine, name="product_line"))
    scope: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    assignee_id: Mapped[str | None] = mapped_column(String(100))
    priority: Mapped[str] = mapped_column(String(16), default="medium")
    status: Mapped[str] = mapped_column(String(32), default="todo")
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    progress: Mapped[int] = mapped_column(default=0)


class Supplier(TimestampMixin, Base):
    __tablename__ = "suppliers"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(32), default="active")
    markets: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    quality_score: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    performance: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)


class Product(TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("supplier_id", "external_code"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_code: Mapped[str] = mapped_column(String(120))
    product_line: Mapped[ProductLine] = mapped_column(Enum(ProductLine, name="product_line"))
    supplier_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("suppliers.id"), index=True)
    name: Mapped[str] = mapped_column(String(240))
    market: Mapped[str] = mapped_column(String(80), index=True)
    attributes: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    data_version: Mapped[int] = mapped_column(default=1)


class ProductPoolEntry(TimestampMixin, Base):
    __tablename__ = "product_pool_entries"
    __table_args__ = (UniqueConstraint("campaign_id", "product_id"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campaigns.id"), index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("products.id"), index=True)
    status: Mapped[PoolStatus] = mapped_column(
        Enum(PoolStatus, name="pool_status"), default=PoolStatus.SOURCING, index=True
    )
    exception_status: Mapped[str | None] = mapped_column(String(40))
    current_grading_result_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    status_reason: Mapped[str | None] = mapped_column(Text)
    version: Mapped[int] = mapped_column(default=1)


class GradingResult(Base):
    __tablename__ = "grading_results"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pool_entry_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("product_pool_entries.id"), index=True
    )
    product_line: Mapped[ProductLine] = mapped_column(Enum(ProductLine, name="product_line"))
    model_version: Mapped[str] = mapped_column(String(80))
    input_version: Mapped[int]
    input_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB)
    dimension_scores: Mapped[dict[str, Any]] = mapped_column(JSONB)
    score: Mapped[Decimal] = mapped_column(Numeric(5, 1))
    grade: Mapped[str] = mapped_column(String(1))
    confidence: Mapped[Decimal] = mapped_column(Numeric(4, 3))
    missing_fields: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    computed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class SupplyTarget(TimestampMixin, Base):
    __tablename__ = "supply_targets"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("campaigns.id"), index=True)
    product_line: Mapped[ProductLine] = mapped_column(Enum(ProductLine, name="product_line"))
    market: Mapped[str] = mapped_column(String(80))
    dimension: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    target_product_count: Mapped[int] = mapped_column(default=0)
    target_inventory: Mapped[int] = mapped_column(default=0)


class Alert(TimestampMixin, Base):
    __tablename__ = "alerts"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("campaigns.id"), index=True)
    type: Mapped[str] = mapped_column(String(80))
    severity: Mapped[str] = mapped_column(String(8), index=True)
    status: Mapped[str] = mapped_column(String(32), default="open")
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    facts: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict)
    owner_id: Mapped[str | None] = mapped_column(String(100))


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    actor_type: Mapped[str] = mapped_column(String(32))
    actor_id: Mapped[str | None] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(120), index=True)
    entity_type: Mapped[str] = mapped_column(String(80), index=True)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    before: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    after: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    reason: Mapped[str | None] = mapped_column(Text)
    request_id: Mapped[str | None] = mapped_column(String(80), index=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class AgentRecommendation(TimestampMixin, Base):
    __tablename__ = "agent_recommendations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tool_name: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(32), default="preview", index=True)
    scope: Mapped[dict[str, Any]] = mapped_column(JSONB)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSONB)
    proposed_action: Mapped[dict[str, Any]] = mapped_column(JSONB)
    base_versions: Mapped[dict[str, Any]] = mapped_column(JSONB)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    confirmed_by: Mapped[str | None] = mapped_column(String(100))
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    execution_result: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
