from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from .structs import *
from utils.mongodb import get_mongo_client
from utils.redis import get_redis_client
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from base64 import b85decode
from uuid import uuid4
import binascii
from utils.utils import image_valid
import logging

recface_router = APIRouter()


@recface_router.post("/recface/", response_class=PlainTextResponse)
async def new_recface(req: FaceRecRequest):
    mongo_client = await get_mongo_client()
    redis_client = await get_redis_client()
    logging.debug("Got all the BD drivers")

    image_bucket = AsyncIOMotorGridFSBucket(mongo_client.image_cache)
    logging.debug("Got a bucket")

    try:
        sent_image = b85decode(req.face)
    except binascii.Error:
        logging.info("Got invalid b85 on new_recface")
        raise HTTPException(status_code=400, detail="Image sent can not be decoded")

    if not image_valid(sent_image):
        logging.info("Got invalid image on new_recface")
        raise HTTPException(status_code=400, detail="Image sent is not valid")

    task_id = uuid4().hex
    await image_bucket.upload_from_stream(task_id, sent_image)

    await redis_client.set(task_id, "PENDING")
    logging.debug("Put task state to redis")

    await redis_client.xadd("corecomp.recface",
                            NewTaskToRedis(task_id=task_id).dict())

    return task_id


@recface_router.get("/recface/{task_id}", response_model=FaceRecResult)
async def get_recface_result(task_id: str):
    redis_client = await get_redis_client()
    mongo_client = await get_mongo_client()

    if await redis_client.exists(task_id) == 0:
        raise HTTPException(status_code=404, detail="No such task")

    result = await redis_client.get(task_id)

    res_arr = result.decode().split()

    if len(res_arr) == 1:
        res_arr.append("")

    state = TaskState(res_arr[0])

    if state in (TaskState.ok, TaskState.failed):
        await redis_client.dump(task_id)
        logging.debug(f"Dumped {task_id}")

    if state in (TaskState.pending, TaskState.failed):
        return FaceRecResult(state=state, message=res_arr[1] if len(res_arr) > 1 else "")
    else:
        resp = mongo_client.recface_resp_cache.find_one({"_id": task_id})
        del resp["_id"]
        await mongo_client.recface_resp_cache.delete_one({"_id": task_id})
        return FaceRecResult(state=state, matches=[PersonInformation(**x) for x in resp])
