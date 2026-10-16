import json

import redis.asyncio as aioredis

from app.configs import config


class RedisService:
    # Init Redis connection
    def __init__(self):
        self.client = aioredis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            password=config.REDIS_PASSWORD or None,
            db=config.REDIS_DB,
            decode_responses=True,
        )

    # Get value from Redis cache
    async def get_from_cache(self, key: str):
        data = await self.client.get(key)
        if data:
            return json.loads(data)

        return None

    # Set value to Redis cache
    async def set_to_cache(self, key: str, value: dict, ttl: int = 3600):
        return await self.client.set(key, json.dumps(value), ex=ttl)

    # Remove value from Redis cache
    async def remove_from_cache(self, key: str):
        return await self.client.delete(key)

    # Close Redis connection
    async def close(self):
        await self.client.close()


redis_service = RedisService()
