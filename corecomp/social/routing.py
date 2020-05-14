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


@social_router.post("/{task_id}", response_model=DefaultResult)
async def check_parsetask(task_id: str):
    redis_client = await get_redis_client()

    if await redis_client.exists(task_id) == 0:
        raise HTTPException(status_code=404, detail="No such task")

    result = await redis_client.get(task_id)

    res_arr = result.decode().split()
    res_state = TaskState(res_arr[0])

    if res_state in (TaskState.ok, TaskState.failed):
        await redis_client.dump(task_id)
        logging.debug(f"Dumped {task_id}")

    return DefaultResult(state=res_state, message=res_arr[1] if len(res_arr) > 1 else "")
