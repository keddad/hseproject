from enum import Enum
from pydantic import BaseModel


class SocialNetwork(str, Enum):
    vk = "VK"
    fb = "FB"
    ok = "OK"


class TaskToRedis(BaseModel):
    network: str
    id: str
    append_face: int

