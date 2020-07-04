from typing import Optional
from utils.db import init_pool
from fastapi import FastAPI
import logging

from router.rec import router as rec_router
from router.add import router as add_router

app = FastAPI()
logging.basicConfig(level=logging.DEBUG, format='%(relativeCreated)6d %(threadName)s %(message)s')

@app.on_event("startup")
async def startup():
    await init_pool()


@app.get("/api/core/generate_204", status_code=204)
def generate_204():
    return


app.include_router(
    rec_router,
    prefix="/api/core"
)

app.include_router(
    add_router,
    prefix="/api/core"
)
