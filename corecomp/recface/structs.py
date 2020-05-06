from typing import List, Optional
from pydantic import BaseModel
from utils.structs import Trait, TaskState


class FaceRecRequest(BaseModel):
    face: str


class PersonInformation(BaseModel):
    probability: float
    traits: List[Trait]


class NewTaskToRedis(BaseModel):
    task_id: str


class FaceRecResult(BaseModel):
    state: TaskState
    message: str = ""
    matches: Optional[List[PersonInformation]]
