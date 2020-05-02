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
async def get_recface_result(
        task_id: str):  # Напишу, когда допишу воркера; Все равно придется решать конфликты формата возврата в могну
    pass