from aioredis import create_redis_pool, ConnectionsPool


class Database:
    client: ConnectionsPool = None


db = Database()


async def connect_to_redis():
    db.client = create_redis_pool("redis://localhost", password="mysweetredis")


async def close_redis_connection():
    db.client.close()
    await db.client.wait_closed()


async def get_redis_client() -> ConnectionsPool:
    return db.client
