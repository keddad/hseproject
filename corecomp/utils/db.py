import asyncpg

pool = None


async def init_pool():
    pool = await asyncpg.create_pool(
        dsn="postgres://postgres:pass@ff_postgres:5432/")

    async with pool.acquire() as con:
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
