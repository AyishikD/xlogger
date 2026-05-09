import asyncio
import json
import logging
from app.core.redis import redis_client
from app.db.session import AsyncSessionLocal
from app.services.relationship_builder import relationship_builder
from app.services.learning_engine import learning_engine
from app.repositories.memory_event import memory_event_repo
from app.models.models import MemoryEvent
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("synthesis_worker")

async def process_memory_events():
    """
    Listen for new memory events and build relationships/learnings.
    """
    logger.info("Synthesis Worker started, listening on 'memory_events_queue'...")
    
    while True:
        try:
            # 1. Dequeue event
            event_json = await redis_client.dequeue_event("memory_events_queue", timeout=5)
            if not event_json:
                continue
                
            event_data = json.loads(event_json)
            event_id = event_data.get("id")
            logger.info(f"Processing event: {event_id}")

            async with AsyncSessionLocal() as db:
                # 2. Fetch full event object
                event = await memory_event_repo.get(db, event_id)
                if not event:
                    logger.warning(f"Event {event_id} not found in DB")
                    continue

                # 3. Build Relationships
                logger.info(f"Building relationships for {event_id}")
                await relationship_builder.build_relationships_for_event(db, event)

                # 4. Check if we should trigger learning synthesis
                # Trigger immediately for CRITICAL events, or after 3 events of same type
                logger.info(f"Checking synthesis for {event_id} (Type: {event.event_type}, Severity: {event.severity})")
                
                sev = getattr(event.severity, "value", str(event.severity)).upper()
                if sev == "CRITICAL":
                    logger.info(f"CRITICAL event detected. Triggering immediate synthesis for {event_id}")
                    await learning_engine.generate_learning_from_cluster(db, [event])
                else:
                    stmt = select(MemoryEvent).where(MemoryEvent.event_type == event.event_type).limit(10)
                    result = await db.execute(stmt)
                    events = result.scalars().all()
                    logger.info(f"Found {len(events)} events of type {event.event_type}")
                    
                    if len(events) >= 3:
                        logger.info(f"Threshold reached for {event.event_type}. Synthesizing learning...")
                        await learning_engine.generate_learning_from_cluster(db, list(events))

        except Exception as e:
            logger.error(f"Error in Synthesis Worker: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(process_memory_events())
