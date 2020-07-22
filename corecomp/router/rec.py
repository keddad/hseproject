from base64 import b85decode
from binascii import Error as BaseDecodeError
from io import BytesIO
from typing import List

import face_recognition
import ujson
from loguru import logger
from PIL import UnidentifiedImageError
from fastapi import APIRouter, HTTPException

from utils.data import FaceRecRequest, PersonInformation, FaceRecResponce, VecRecRequest
from utils.db import db

router = APIRouter()

SEARCH_QUERY = '''
            SELECT
            traits, 
            SQRT(
                POWER(CUBE($1::double precision[]) <-> vec_low, 2) 
                + POWER(CUBE($2::double precision[]) <-> vec_high, 2)
            ) AS probability
            FROM vector
            ORDER BY 
            SQRT(
                POWER(CUBE($1::double precision[]) <-> vec_low, 2) 
                + POWER(CUBE($2::double precision[]) <-> vec_high, 2)
            ) ASC LIMIT 5
            '''


@router.get("/recface/", response_model=List[FaceRecResponce])
async def recface(req: FaceRecRequest):
    try:
        face = face_recognition.load_image_file(
            BytesIO(
                b85decode(req.face)
            )
        )
    except BaseDecodeError:
        logger.warning("Recface request failed, unable to decode Base85")
        raise HTTPException(status_code=400, detail="Can't decode Base85")
    except UnidentifiedImageError:
        logger.warning("Recface request failed, unable to read image")
        raise HTTPException(status_code=400, detail="Broken image file")

    features = face_recognition.face_encodings(face)

    if len(features) == 0:
        logger.warning("Recface request failed, no faces found on image")
        raise HTTPException(status_code=400, detail="No faces found on image")

    raw_res = []

    async with db.pool.acquire() as conn:
        await conn.set_type_codec(
            'json',
            encoder=ujson.dumps,
            decoder=ujson.loads,
            schema='pg_catalog'
        )

        for vec in features:
            vec_matches = await conn.fetch(SEARCH_QUERY, vec[0:64], vec[64:128])
            raw_res.append(vec_matches)

    for i in range(0, len(raw_res)):
        for j in range(0, len(raw_res[i])):
            raw_res[i][j] = PersonInformation(
                traits=raw_res[i][j]["traits"], probability=raw_res[i][j]["probability"])

    resp_list = list([FaceRecResponce(matches=x) for x in raw_res])
    return resp_list


@router.get("/recvec/", response_model=FaceRecResponce)
async def recvec(req: VecRecRequest):
    pass
