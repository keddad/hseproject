from pydantic import BaseModel
from typing import List, Dict



class FaceAddRequest(BaseModel):
    face: str
    traits: Dict[str, List[str]]


class FaceRecRequest(BaseModel):
    face: str


class VecRecRequest(BaseModel):
    face: List[float]


class PersonInformation(BaseModel):
    traits: Dict[str, List[str]]
    probability: float


class FaceRecResponce(BaseModel):
    matches: List[PersonInformation]
