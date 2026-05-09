import uuid
import json
from typing import List, Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas import schemas
from app.repositories.memory_event import memory_event_repo
from app.services.embedding import embedding_service
from app.core.redis import redis_client

router = APIRouter()

@router.post("/ingest", response_model=schemas.MemoryEvent)
async def ingest_memory_event(
    event_in: schemas.MemoryEventCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Ingest a new ML memory event.
    Generates embedding and stores in DB.
    Also enqueues for background processing.
    """
    # 1. Generate embedding
    embedding = await embedding_service.generate_embedding(event_in.summary)
    
    # 2. Create in DB
    db_obj = await memory_event_repo.create(db, obj_in=event_in)
    
    # 3. Add embedding
    db_obj.embedding = embedding
    await db.commit()
    await db.refresh(db_obj)
    
    # 4. Enqueue for background workers (e.g. relationship building)
    event_data = {
        "id": str(db_obj.id),
        "event_type": db_obj.event_type,
        "summary": db_obj.summary
    }
    await redis_client.enqueue_event("memory_events_queue", json.dumps(event_data))
    return db_obj

@router.get("/all", response_model=List[schemas.MemoryEvent])
async def get_all_events(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    """
    Retrieve all historical memory events.
    """
    return await memory_event_repo.get_multi(db, skip=skip, limit=limit)

@router.post("/find_similar", response_model=List[schemas.MemoryEventSimilarityResult])
async def find_similar_events(
    search_params: schemas.MemoryEventSearch,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Find semantically similar historical memory events.
    """
    # 1. Generate embedding for query
    query_embedding = await embedding_service.generate_embedding(search_params.summary)
    
    # 2. Search in pgvector
    results = await memory_event_repo.find_similar(
        db, 
        embedding=query_embedding,
        event_type=search_params.event_type,
        limit=search_params.limit
    )
    
    # 3. Format response
    formatted_results = []
    for event, similarity in results:
        # Pydantic model conversion
        event_dict = schemas.MemoryEvent.model_validate(event).model_dump()
        event_dict["similarity_score"] = float(similarity)
        formatted_results.append(event_dict)
        
    return formatted_results

@router.post("/extract_events", response_model=schemas.ExtractEventsResponse)
async def extract_events(
    request: schemas.ExtractEventsRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Extract canonical events from raw logs/text.
    If experiment_id is provided, automatically links and stores them.
    """
    from app.events.extractors.registry import extractor_registry
    from app.repositories.experiment import experiment_repo
    
    extracted_results = extractor_registry.extract_all(request.text)
    saved_events = []
    
    for res in extracted_results:
        # Create event object
        event_data = schemas.MemoryEventCreate(
            experiment_id=request.experiment_id or uuid.uuid4(), # Placeholder if no exp
            event_type=res.event_type,
            severity=res.severity,
            summary=res.summary,
            content=res.content,
            metadata_json=res.metadata
        )
        
        # If experiment exists, use repository to save
        if request.experiment_id:
            db_obj = await memory_event_repo.create(db, obj_in=event_data)
            # Generate embedding
            embedding = await embedding_service.generate_embedding(db_obj.summary)
            db_obj.embedding = embedding
            await db.commit()
            await db.refresh(db_obj)
            saved_events.append(db_obj)
        else:
            # Just return the extracted info (as MemoryEvent schema)
            # In real prod, we'd probably require an experiment_id
            pass
            
    return {"events": saved_events}

@router.post("/analyze_failure", response_model=schemas.FailureAnalysisResponse)
async def analyze_failure(
    request: schemas.FailureAnalysisRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Infer likely causes of a failure event.
    """
    from app.services.root_cause_engine import root_cause_engine
    result = await root_cause_engine.analyze_failure(db, str(request.event_id))
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/build_relationships")
async def build_relationships(
    request: schemas.BuildRelationshipsRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Manually trigger relationship building for an event.
    """
    from app.services.relationship_builder import relationship_builder
    event = await memory_event_repo.get(db, request.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    await relationship_builder.build_relationships_for_event(db, event)
    return {"status": "success"}

@router.get("/graph")
async def get_memory_graph(
    db: AsyncSession = Depends(get_db)
) -> Any:
    from app.repositories.experiment import experiment_repo
    from app.repositories.relationship import relationship_repo
    from app.models.models import MemoryEvent, Learning
    from app.models.enums import Severity
    
    exps = await experiment_repo.get_multi(db, limit=100)
    rels = await relationship_repo.get_multi(db, limit=500)
    
    critical_events_stmt = select(MemoryEvent).where(MemoryEvent.severity == Severity.CRITICAL).limit(50)
    crit_res = await db.execute(critical_events_stmt)
    critical_events = crit_res.scalars().all()

    learnings_stmt = select(Learning).limit(20)
    learn_res = await db.execute(learnings_stmt)
    learnings = learn_res.scalars().all()

    nodes = []
    # Experiments (Blue)
    for i, exp in enumerate(exps):
        nodes.append({
            "id": f"exp_{exp.id}",
            "type": "input",
            "position": {"x": 100 + (i * 450), "y": 50},
            "data": {"label": f"🔬 {exp.name}"},
            "style": {"background": "#1e293b", "color": "#f8fafc", "borderRadius": "12px", "padding": "10px", "border": "2px solid #3b82f6", "width": 200}
        })
    
    # Critical Events (Red)
    for i, event in enumerate(critical_events):
        nodes.append({
            "id": f"evt_{event.id}",
            "position": {"x": 150 + (i % 5 * 300), "y": 350 + (i // 5 * 200)},
            "data": {"label": f"⚠️ {event.event_type.value}"},
            "style": {"background": "#450a0a", "color": "#fca5a5", "borderRadius": "8px", "padding": "8px", "border": "1px solid #ef4444", "width": 180}
        })

    # Learnings (Green)
    for i, learn in enumerate(learnings):
        nodes.append({
            "id": f"lrn_{learn.id}",
            "position": {"x": 200 + (i * 400), "y": 750},
            "data": {"label": f"🧠 {learn.title}"},
            "style": {"background": "#064e3b", "color": "#6ee7b7", "borderRadius": "12px", "padding": "12px", "border": "2px solid #10b981", "width": 220}
        })
        
    edges = []
    # Experiment -> Event
    for event in critical_events:
        edges.append({
            "id": f"e_exp_evt_{event.id}",
            "source": f"exp_{event.experiment_id}",
            "target": f"evt_{event.id}",
            "label": "contains",
            "animated": True,
            "style": {"stroke": "#475569"}
        })

    # Event -> Event (Causal/Similarity)
    for rel in rels:
        edges.append({
            "id": str(rel.id),
            "source": f"evt_{rel.source_id}",
            "target": f"evt_{rel.target_id}",
            "label": rel.relationship_type.value,
            "style": {"stroke": "#3b82f6", "strokeDasharray": "5,5"}
        })

    # Event -> Learning (Synthesized)
    for learn in learnings:
        supporting_events = learn.metadata_json.get("supporting_events", [])
        for evt_id in supporting_events:
            edges.append({
                "id": f"e_evt_lrn_{evt_id}_{learn.id}",
                "source": f"evt_{evt_id}",
                "target": f"lrn_{learn.id}",
                "label": "synthesized",
                "animated": True,
                "style": {"stroke": "#10b981"}
            })
                
    return {"nodes": nodes, "edges": edges}

