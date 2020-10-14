import aiohttp
import asyncio
from ss import ids # подписчики лицейского вконтача
from collections import Counter

async def process_id(id: int, sem):
    await sem.acquire()
    async with aiohttp.ClientSession() as session:
        async with session.post(f"http://localhost/api/parse/VK/{id}") as r:
            sem.release()
            return r.status


async def main():
    sem = asyncio.Semaphore(32) # то на чем работает сервер перегружается только в путь
    print(
        Counter(
            await asyncio.gather(
                *[process_id(i, sem) for i in ids]
            )
        )
    )

asyncio.run(main())
