from typing import Optional
from utils.db import init_pool
from fastapi import FastAPI

app = FastAPI()


@app.on_event("startup")
async def startup():
    await init_pool()


@app.get("/api/home")
def read_root():
    return {"Hello": "World"}
