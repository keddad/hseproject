from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from .structs import *
from utils.structs import *
from utils.redis import get_redis_client
import logging
from uuid import uuid4

social_router = APIRouter()


@social_router.post("/{network}/{page_id}/", response_class=PlainTextResponse)
async def new_parsetask(network: SocialNetwork, page_id: str, skip_existing: bool = False):
    redis_client = await get_redis_client()

    task_id = uuid4().hex

    await redis_client.set(task_id, "PENDING")
    await redis_client.xadd("socialcomp.parse",
                            TaskToRedis(network=network.name, id=page_id,
                                        append_face=(1 if skip_existing else 0)).dict())

    return task_id
