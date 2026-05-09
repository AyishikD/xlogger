import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict
from app.models.enums import EventType, Severity, LearningType


class ExperimentBase(BaseModel):
    name: str
    description: Optional[str] = None
    metadata_json: Dict[str, Any] = {}


class ExperimentCreate(ExperimentBase):
    pass


class Experiment(ExperimentBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MemoryEventBase(BaseModel):
    experiment_id: uuid.UUID
    event_type: EventType
    severity: Severity = Severity.INFO
    summary: str
    content: Optional[str] = None
    metadata_json: Dict[str, Any] = {}


class MemoryEventCreate(MemoryEventBase):
    pass


class MemoryEvent(MemoryEventBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    # We don't return the raw embedding to the user usually
    
    model_config = ConfigDict(from_attributes=True)


class MemoryEventSearch(BaseModel):
    summary: str
    event_type: Optional[EventType] = None
    limit: int = 5


class MemoryEventSimilarityResult(MemoryEvent):
    similarity_score: float

    model_config = ConfigDict(from_attributes=True)


class ExtractEventsRequest(BaseModel):
    text: str
    experiment_id: Optional[uuid.UUID] = None


class ExtractEventsResponse(BaseModel):
    events: List[MemoryEvent]


class FailureAnalysisRequest(BaseModel):
    event_id: uuid.UUID


class FailureAnalysisResponse(BaseModel):
    event_summary: str
    likely_causes: List[str]
    confidence: float
    supporting_events: List[Dict[str, Any]]
    shared_patterns: List[str]
    recommended_actions: List[str]


class BuildRelationshipsRequest(BaseModel):
    event_id: uuid.UUID


class LearningGenerateRequest(BaseModel):
    event_ids: List[uuid.UUID]
    learning_type: LearningType = LearningType.FAILURE_PATTERN


class ExperimentCompareRequest(BaseModel):
    experiment_id_a: uuid.UUID
    experiment_id_b: uuid.UUID


class TimelineEntry(BaseModel):
    timestamp: str
    event_id: str
    type: str
    severity: str
    summary: str
    meta: Dict[str, Any]
    relationships: Optional[List[Dict[str, Any]]] = None


class TimelineResponse(BaseModel):
    experiment_id: uuid.UUID
    timeline: List[TimelineEntry]


class StreamMetricsRequest(BaseModel):
    experiment_id: uuid.UUID
    metrics: Dict[str, float]


class PredictFailureRequest(BaseModel):
    experiment_id: uuid.UUID
    current_metrics: Dict[str, float]


class RecommendInterventionRequest(BaseModel):
    experiment_id: uuid.UUID
    failure_type: str
    current_state: Dict[str, Any]


class PostmortemResponse(BaseModel):
    experiment_name: str
    generated_at: str
    summary: str
    status: str
    failure_timeline: List[Dict[str, Any]]
    root_cause_analysis: Dict[str, Any]
    recurrence_metrics: Dict[str, Any]
    organizational_impact: str
    action_items: List[str]


class LearningBase(BaseModel):
    title: str
    content: str
    metadata_json: Dict[str, Any] = {}
    event_id: Optional[uuid.UUID] = None


class LearningCreate(LearningBase):
    pass


class LearningUpdate(LearningBase):
    title: Optional[str] = None
    content: Optional[str] = None


class Learning(LearningBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RecommendationFeedbackRequest(BaseModel):
    experiment_id: uuid.UUID
    learning_id: Optional[uuid.UUID] = None
    action_taken: str
    was_successful: bool
    metrics_delta: Dict[str, Any] = {}
