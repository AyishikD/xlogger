from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.redis import redis_client

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    origins = [str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS]
    print(f"DEBUG: Allowed CORS Origins: {origins}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

@app.on_event("startup")
async def startup_event():
    await redis_client.connect()
    from app.websockets.manager import ws_manager
    from app.workers.synthesis_worker import process_memory_events
    asyncio.create_task(ws_manager.stream_from_redis())
    asyncio.create_task(process_memory_events())

@app.on_event("shutdown")
async def shutdown_event():
    await redis_client.disconnect()

app.include_router(api_router, prefix=settings.API_V1_STR)

from app.api.v1.endpoints import websockets
app.include_router(websockets.router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.ENVIRONMENT}
