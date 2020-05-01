from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from .structs import *
from utils.mongodb import get_mongo_client
from utils.redis import get_redis_client
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from base64 import b85decode
from uuid import uuid4
from aio_pika import Message
import binascii
from utils.utils import image_valid
import logging

addface_router = APIRouter()


@addface_router.post("/addface/", response_class=PlainTextResponse)
async def new_addface(req: FaceAddBody, append_face: bool = True):
    mongo_client = await get_mongo_client()
    redis_client = await get_redis_client()
    logging.debug("Got all the BD drivers")

    image_bucket = AsyncIOMotorGridFSBucket(mongo_client.image_cache)
    logging.debug("Got a bucket")

    try:
        sent_image = b85decode(req.face)
    except binascii.Error:
        logging.info("Got invalid b85 on new_addface")
        raise HTTPException(status_code=400, detail="Image sent can not be decoded")

    if not image_valid(sent_image):
        logging.info("Got invalid image on new_addface")
        raise HTTPException(status_code=400, detail="Image sent is not valid")

    task_id = uuid4().hex
    image_id = await image_bucket.upload_from_stream(task_id, sent_image)

    to_mongo = req.dict()
    to_mongo.pop("face", None)
    trait_id = await mongo_client.caches.traits.insert_one(to_mongo)

    logging.debug("Got image and trait id")
    logging.debug(f"image_id:{image_id}, trait_id:{trait_id}")

    await redis_client.set(task_id, "PENDING")

    logging.debug("Put task state to redis")

    await redis_client.xadd("corecomp.addface",
                            NewFaceToRedis(image_id=str(image_id), task_id=task_id,
                                           trait_id=str(trait_id.inserted_id),
                                           append=str(append_face)).dict())

    logging.debug(f"Put task to redis stream")

    return task_id


@addface_router.get("/addface/{task_id}", response_model=FaceAddResult)
async def get_addface_result(task_id: str):
    redis_client = await get_redis_client()

    if await redis_client.exists(task_id) == 0:
        raise HTTPException(status_code=404, detail="No such task")

    result = await redis_client.get(task_id)
    res_arr = result.split()

    res_arr = list(map(lambda x: x.decode(), res_arr))

    logging.debug(f"{res_arr} is a res of get_addface_res for {task_id}")

    if len(res_arr) > 1:
        return FaceAddResult(message=res_arr[1], state=FaceAddState(res_arr[0]))

    else:
        logging.debug("Got to status only reply on addface")
        return FaceAddResult(state=FaceAddState(res_arr[0]))