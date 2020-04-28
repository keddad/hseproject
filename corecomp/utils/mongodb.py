from motor.motor_asyncio import AsyncIOMotorClient


class Database:
    client: AsyncIOMotorClient = None


db = Database()


async def connect_to_mongo():
    db.client = AsyncIOMotorClient("mongodb://ff_mongodb:27017")


async def close_mongo_connection():
    db.client.close()


async def get_mongo_client() -> AsyncIOMotorClient:
    return db.client
