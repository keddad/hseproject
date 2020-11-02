from fastapi import FastAPI, HTTPException
from utils import *
import tempfile
from base64 import b85decode
import asyncio
import binascii
from loguru import logger
import numpy as np
import cv2
import uvicorn
from face_recognition import face_encodings, face_distance

app = FastAPI()

THRESHOLD = 0.6


@app.post("/api/video", response_model=List[List[Dict]])
async def process(vid: VideoMessage):
    try:
        decoded_vid = b85decode(vid.video)
        tfile = tempfile.NamedTemporaryFile()
        tfile.write(decoded_vid)
        del decoded_vid
    except binascii.Error:
        raise HTTPException(status_code=400, detail="Your b85 encoding is broken")

    try:
        cap = cv2.VideoCapture(tfile.name)
    except cv2.error:
        raise HTTPException(status_code=400, detail="Your video encoding is as not cv2-readable")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    logger.info(f"Got video, {frame_width}x{frame_height}, {frame_count}")

    buf = np.empty((frame_height, frame_width, 3), np.dtype(
        'uint8'))

    fc = 0
    ret = True

    face_vectors = []

    while fc < frame_count and ret:
        ret, buf = cap.read()
        fc += 1

        encodings = face_encodings(buf)

        for face in encodings:
            distances = face_distance(face_vectors, face)
            for ans in distances:
                if ans <= THRESHOLD:
                    break
            else:
                face_vectors.append(face)

    coros = (get_matches_for_user(list(u)) for u in face_vectors)
    results = await asyncio.gather(*coros, return_exceptions=True)

    output = []
    for res in results:
        if isinstance(res, Exception):
            logger.warning(f"{res} while fetching corecomp answers")
            continue
        output.append(res)

    return output


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)  # To debug outside of container
