from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas import schemas
from app.repositories.experiment import experiment_repo

router = APIRouter()

@router.get("/", response_model=List[schemas.Experiment])
async def read_experiments(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    return await experiment_repo.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=schemas.Experiment)
async def create_experiment(
    experiment_in: schemas.ExperimentCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    return await experiment_repo.create(db, obj_in=experiment_in)

@router.get("/{id}", response_model=schemas.Experiment)
async def read_experiment(
    id: str,
    db: AsyncSession = Depends(get_db)
) -> Any:
    experiment = await experiment_repo.get(db, id=id)
    if not experiment:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment
