from typing import List, Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas import schemas
from app.services.live_monitor import live_monitor
from app.services.failure_predictor import failure_predictor
from app.services.intervention_engine import intervention_engine
from app.services.event_stream import event_stream
from app.services.postmortem_generator import postmortem_generator

router = APIRouter()

@router.post("/stream_metrics")
async def stream_metrics(
    request: schemas.StreamMetricsRequest,
) -> Any:
    """
    Stream live metrics for an experiment.
    Triggers live anomaly detection.
    """
    alerts = await live_monitor.process_metrics(str(request.experiment_id), request.metrics)
    await event_stream.publish_metric(str(request.experiment_id), request.metrics)
    return {"status": "success", "alerts_triggered": len(alerts)}

@router.post("/predict_failure")
async def predict_failure(
    request: schemas.PredictFailureRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Predict likely failures based on current metrics and recent events.
    """
    from app.repositories.memory_event import memory_event_repo
    # Fetch recent events for the experiment
    # (Simplified: fetch last 5 events)
    recent_events = await memory_event_repo.get_multi(db, limit=5) 
    
    prediction = await failure_predictor.predict_failure(
        str(request.experiment_id), 
        recent_events, 
        request.current_metrics
    )
    return prediction

@router.post("/recommend_intervention")
async def recommend_intervention(
    request: schemas.RecommendInterventionRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Recommend corrective actions for a potential or current failure.
    """
    result = await intervention_engine.recommend_intervention(
        db,
        str(request.experiment_id),
        request.failure_type,
        request.current_state
    )
    return result

@router.get("/live_alerts")
async def get_live_alerts(count: int = 20) -> Any:
    """
    Get most recent live alerts from the cognition stream.
    """
    return await event_stream.get_live_alerts(count)

@router.post("/send_command/{experiment_id}")
async def send_command(experiment_id: str, command: Dict[str, Any]):
    """Send a manual intervention command to a running experiment."""
    from app.websockets.manager import ws_manager
    await ws_manager.send_to_experiment(experiment_id, command)
    return {"status": "sent", "command": command}

@router.post("/log_outcome")
async def log_outcome(
    request: schemas.RecommendationFeedbackRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Log the outcome of an intervention to improve future confidence.
    """
    from app.models.models import RecommendationOutcome
    
    outcome = RecommendationOutcome(
        experiment_id=request.experiment_id,
        learning_id=request.learning_id,
        action_taken=request.action_taken,
        was_successful=request.was_successful,
        metrics_delta=request.metrics_delta
    )
    db.add(outcome)
    await db.commit()
    return {"status": "success", "recorded": True}

@router.get("/postmortem/{experiment_id}", response_model=schemas.PostmortemResponse)
async def get_postmortem(
    experiment_id: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Generate an automated research postmortem for an experiment.
    """
    postmortem = await postmortem_generator.generate_postmortem(db, experiment_id)
    if "error" in postmortem:
        raise HTTPException(status_code=404, detail=postmortem["error"])
    return postmortem
