import redis.asyncio as redis
from app.core.config import settings

class RedisClient:
    def __init__(self):
        self.redis: redis.Redis | None = None

    async def connect(self):
        self.redis = redis.from_url(
            settings.REDIS_URL, 
            encoding="utf-8", 
            decode_responses=True
        )

    async def disconnect(self):
        if self.redis:
            await self.redis.close()

    async def enqueue_event(self, queue_name: str, data: str):
        if not self.redis:
            await self.connect()
        await self.redis.lpush(queue_name, data)

    async def dequeue_event(self, queue_name: str, timeout: int = 0):
        if not self.redis:
            await self.connect()
        result = await self.redis.brpop(queue_name, timeout=timeout)
        if result:
            return result[1]
        return None

    async def get(self, key: str):
        if not self.redis:
            await self.connect()
        return await self.redis.get(key)

    async def set(self, key: str, value: str, ex: int | None = None):
        if not self.redis:
            await self.connect()
        return await self.redis.set(key, value, ex=ex)

redis_client = RedisClient()

async def get_redis():
    if not redis_client.redis:
        await redis_client.connect()
    return redis_client.redis
