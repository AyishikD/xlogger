from fastapi import APIRouter
from app.api.v1.endpoints import experiments, memory_events, learning, monitor, launchpad

api_router = APIRouter()
api_router.include_router(experiments.router, prefix="/experiments", tags=["experiments"])
api_router.include_router(memory_events.router, prefix="/memory", tags=["memory"])
api_router.include_router(learning.router, prefix="/learning", tags=["learning"])
api_router.include_router(monitor.router, prefix="/monitor", tags=["monitor"])
api_router.include_router(launchpad.router, prefix="/launchpad", tags=["launchpad"])
