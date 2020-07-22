from base64 import b85decode
from io import BytesIO
from binascii import Error as BaseDecodeError
from PIL import UnidentifiedImageError

import face_recognition
from loguru import logger
import ujson
from fastapi import APIRouter, HTTPException

from utils.data import FaceAddRequest
from utils.db import db

router = APIRouter()


@router.post("/addface/", status_code=200)
async def addface(req: FaceAddRequest):
    try:
        face = face_recognition.load_image_file(
            BytesIO(
                b85decode(req.face)
            )
        )
    except BaseDecodeError:
        logger.warning("Addface request failed, unable to decode Base85")
        raise HTTPException(status_code=400, detail="Can't decode Base85")
    except UnidentifiedImageError:
        logger.warning("Addface request failed, unable to read image")
        raise HTTPException(status_code=400, detail="Broken image file")

    features = face_recognition.face_encodings(face)

    if len(features) == 0:
        logger.warning("Addface request failed, no faces found on image")
        raise HTTPException(status_code=400, detail="No faces found on image")

    async with db.pool.acquire() as conn:
        await conn.set_type_codec(
            'json',
            encoder=ujson.dumps,
            decoder=ujson.loads,
            schema='pg_catalog'
        )

        for vec in features:
            await conn.execute('''
                INSERT INTO vector (traits, vec_low, vec_high) VALUES ($1, CUBE($2::double precision[]), CUBE($3::double precision[]))
                ''', req.traits, vec[0:64], vec[64:128]
                               )
