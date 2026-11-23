from redis.asyncio import Redis

from app.config import settings

redis_client: Redis | None = None


async def init_redis():
    global redis_client
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None
