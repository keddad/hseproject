from pydantic import BaseModel
from typing import List


class Trait(BaseModel):
    name: str
    options: List[str]


class FaceAddRequest(BaseModel):
    face: str
    options: List[Trait]


class FaceRecRequest(BaseModel):
    face: str
