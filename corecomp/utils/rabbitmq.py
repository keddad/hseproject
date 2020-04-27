from aio_pika import connect, Channel
from aio_pika.connection import Connection


class Database:
    client: Connection = None


db = Database()


async def connect_to_rabbitmq():
    db.client = connect("amqp://user:mysweetrabbit@rabbitq")


async def close_rabbitmq_connection():
    await db.client.close()


async def get_rabbitmq_channel() -> Channel:
    return await db.client.channel()
