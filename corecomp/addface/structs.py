from typing import List
from pydantic import BaseModel, validator
from utils.structs import Trait, TaskState


class NewFaceToRedis(BaseModel):
    task_id: str
    append: int


class FaceAddBody(BaseModel):
    face: str
    traits: List[Trait]

    @validator("traits")
    def traits_non_empty(cls, v):
        assert len(v) > 0
        return v


class FaceAddResult(BaseModel):
    message: str = ""
    state: TaskState
