from fastapi import FastAPI
from utils.mongodb import connect_to_mongo, close_mongo_connection
from utils.redis import connect_to_redis, close_redis_connection
import logging
from time import sleep
from addface.routing import addface_router
from recface.routing import recface_router
from social.routing import social_router

app = FastAPI()
logging.basicConfig(level=logging.DEBUG, format="%(asctime)-15s %(message)s")


@app.get("/isalive")
def read_root():
    return "ok"


app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)

app.add_event_handler("startup", connect_to_redis)
app.add_event_handler("shutdown", close_redis_connection)

app.include_router(
    addface_router,
    prefix="/api/task"
)

app.include_router(
    recface_router,
    prefix="/api/task"
)

app.include_router(
    social_router,
    prefix="/api/parse"
)
