import asyncpg
from loguru import logger


class Database:
    pool: asyncpg.pool.Pool = None


db = Database()


async def init_pool():
    db.pool = await asyncpg.create_pool(
        dsn="postgres://postgres:pass@ff_postgres:5432/")

    async with db.pool.acquire() as con:
        await con.execute(
            '''
            CREATE EXTENSION IF NOT EXISTS cube;
            '''
        )
        await con.execute(
            '''
            CREATE TABLE IF NOT EXISTS vector (id serial, traits json, vec_low cube, vec_high cube);
            '''
        )

    logger.debug("Dispatched asyncpg pool")
