from typing import List
from pydantic import BaseModel, validator, Field
from enum import Enum


class Trait(BaseModel):
    name: str
    options: List[str]

    @validator("options")
    def options_non_empty(cls, v):
        assert len(v) > 0
        return v


class NewFaceToRedis(BaseModel):
    image_id: str
    task_id: str
    trait_id: str
    append: str


class FaceAddBody(BaseModel):
    face: str
    traits: List[Trait]

    @validator("traits")
    def traits_non_empty(cls, v):
        assert len(v) > 0
        return v


class FaceAddState(str, Enum):
    pending = "PENDING"
    failed = "FAILED"
    ok = "OK"


class FaceAddResult(BaseModel):
    message: str = ""
    state: FaceAddState = FaceAddState.ok
