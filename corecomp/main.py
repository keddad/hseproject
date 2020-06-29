from typing import Optional

from fastapi import FastAPI

app = FastAPI()


@app.get("/api/home")
def read_root():
    return {"Hello": "World"}
