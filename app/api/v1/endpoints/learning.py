from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas import schemas
from app.services.learning_engine import learning_engine
from app.services.diff_engine import diff_engine
from app.services.timeline_builder import timeline_builder
from app.services.memory_evolution import memory_evolution
from app.repositories.memory_event import memory_event_repo
from app.repositories.experiment import experiment_repo

router = APIRouter()

@router.get("/all", response_model=List[schemas.Learning])
async def get_all_learnings(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve all synthesized organizational learnings.
    """
    from app.repositories.learning import learning_repo
    return await learning_repo.get_multi(db, skip=skip, limit=limit)

@router.get("/timeline/{experiment_id}", response_model=schemas.TimelineResponse)
async def get_experiment_timeline(
    experiment_id: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get chronological experiment memory timeline.
    """
    timeline = await timeline_builder.build_experiment_timeline(db, experiment_id)
    return {"experiment_id": experiment_id, "timeline": timeline}

@router.post("/generate_learning")
async def generate_learning(
    request: schemas.LearningGenerateRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Aggregate specific events into organizational learning.
    """
    events = []
    for eid in request.event_ids:
        event = await memory_event_repo.get(db, eid)
        if event:
            events.append(event)
            
    if not events:
        raise HTTPException(status_code=404, detail="No valid events found")
        
    learning = await learning_engine.generate_learning_from_cluster(
        db, events, learning_type=request.learning_type
    )
    return {"status": "success", "learning_id": str(learning.id)}

@router.post("/compare_experiments")
async def compare_experiments(
    request: schemas.ExperimentCompareRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Compare two experiments to identify regressions/improvements.
    """
    exp_a = await experiment_repo.get(db, request.experiment_id_a)
    exp_b = await experiment_repo.get(db, request.experiment_id_b)
    
    if not exp_a or not exp_b:
        raise HTTPException(status_code=404, detail="One or both experiments not found")
        
    comparison = await diff_engine.compare_experiments(exp_a, exp_b)
    return comparison

@router.post("/feedback")
async def record_feedback(
    request: schemas.RecommendationFeedbackRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Record feedback on whether a recommendation actually worked.
    This closes the loop for self-improving debugging intelligence.
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
    
    # Optional: trigger re-weighting of recommendations
    return {"status": "success", "message": "Feedback recorded. Intelligence updated."}
