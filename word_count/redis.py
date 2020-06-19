import aioredis

from settings import REDIS_HOST, REDIS_PORT


class RedisConnection:
    """
    Singleton class providing agents with a connection to the Redis backend.
    """
    _connection = None

    @classmethod
    async def get(cls):
        if cls._connection is None:
            cls._connection = await aioredis.create_redis_pool(
                address=(REDIS_HOST, REDIS_PORT),
                encoding='utf-8'
            )
        return cls._connection
