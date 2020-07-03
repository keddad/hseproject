from fastapi import APIRouter, HTTPException
from utils.data import FaceAddRequest
from utils.db import db
from base64 import b85decode
import face_recognition
import ujson
from io import BytesIO

router = APIRouter()


@router.post("/addface/", status_code=200)
async def addface(req: FaceAddRequest):
    face = face_recognition.load_image_file(
        BytesIO(
            b85decode(req.face)
        )
    )

    features = face_recognition.face_encodings(face)

    if len(features) == 0:
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
