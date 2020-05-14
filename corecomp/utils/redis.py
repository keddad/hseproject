from aioredis import create_redis_pool, Redis
import logging


class Database:
    client: Redis = None


db = Database()


async def connect_to_redis():
    db.client = await create_redis_pool("redis://ff_redis")


async def close_redis_connection():
    db.client.close()
    await db.client.wait_closed()


async def get_redis_client() -> Redis:
    logging.debug("Dispatched redis connection")
    return db.client
