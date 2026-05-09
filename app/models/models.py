import uuid
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.db.base_class import Base, TimestampMixin, UUIDMixin
from app.models.enums import EventType, Severity, ArtifactType, RelationshipType
from app.core.config import settings


class Experiment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "experiments"

    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Relationships
    events: Mapped[List["MemoryEvent"]] = relationship(back_populates="experiment", cascade="all, delete-orphan")


class MemoryEvent(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "memory_events"

    experiment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("experiments.id", ondelete="CASCADE"), index=True)
    event_type: Mapped[EventType] = mapped_column(SQLEnum(EventType), index=True)
    severity: Mapped[Severity] = mapped_column(SQLEnum(Severity), default=Severity.INFO)
    summary: Mapped[str] = mapped_column(String(1000))
    content: Mapped[Optional[str]] = mapped_column(String)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Vector embedding
    embedding: Mapped[Optional[Vector]] = mapped_column(Vector(settings.VECTOR_DIMENSION))

    # Relationships
    experiment: Mapped["Experiment"] = relationship(back_populates="events")
    artifacts: Mapped[List["Artifact"]] = relationship(back_populates="event", cascade="all, delete-orphan")
    source_relationships: Mapped[List["Relationship"]] = relationship(
        foreign_keys="Relationship.source_id", back_populates="source_event"
    )
    target_relationships: Mapped[List["Relationship"]] = relationship(
        foreign_keys="Relationship.target_id", back_populates="target_event"
    )


class Artifact(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "artifacts"

    event_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("memory_events.id", ondelete="CASCADE"), index=True)
    artifact_type: Mapped[ArtifactType] = mapped_column(SQLEnum(ArtifactType))
    uri: Mapped[str] = mapped_column(String(1024))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

    # Relationships
    event: Mapped["MemoryEvent"] = relationship(back_populates="artifacts")


class Relationship(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "relationships"

    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("memory_events.id", ondelete="CASCADE"), index=True)
    target_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("memory_events.id", ondelete="CASCADE"), index=True)
    relationship_type: Mapped[RelationshipType] = mapped_column(SQLEnum(RelationshipType))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

    # Relationships
    source_event: Mapped["MemoryEvent"] = relationship(foreign_keys=[source_id], back_populates="source_relationships")
    target_event: Mapped["MemoryEvent"] = relationship(foreign_keys=[target_id], back_populates="target_relationships")


class Learning(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "learnings"

    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(String)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    
    # Optional link to event that triggered this learning
    event_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("memory_events.id"), nullable=True)
    
    # Vector embedding for retrieval
    embedding: Mapped[Optional[Vector]] = mapped_column(Vector(settings.VECTOR_DIMENSION))


class RecommendationOutcome(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "recommendation_outcomes"

    learning_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("learnings.id"), nullable=True)
    experiment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("experiments.id", ondelete="CASCADE"), index=True)
    action_taken: Mapped[str] = mapped_column(String(255))
    was_successful: Mapped[bool] = mapped_column(default=True)
    metrics_delta: Mapped[dict] = mapped_column(JSON, default=dict)
