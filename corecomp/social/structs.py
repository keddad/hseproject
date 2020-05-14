from enum import Enum
from pydantic import BaseModel


class SocialNetwork(str, Enum):
    vk = "VK"
    fb = "FB"
    ok = "OK"

    def __str__(self):
        return str(self.value)


class TaskToRedis(BaseModel):
    network: str
    id: str
    append_face: int
