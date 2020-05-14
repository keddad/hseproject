from pydantic import BaseModel, validator
from typing import List
from enum import Enum


class Trait(BaseModel):
    name: str
    options: List[str]

    @validator("options")
    def options_non_empty(cls, v):
        assert len(v) > 0
        return v


class TaskState(str, Enum):
    pending = "PENDING"
    failed = "FAILED"
    ok = "OK"

    def __str__(self):
        return str(self.value)


class DefaultResult(BaseModel):
    message: str = ""
    state: TaskState
