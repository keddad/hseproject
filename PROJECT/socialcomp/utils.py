from pydantic import BaseModel
from typing import List, Dict

class BadID(Exception):
    pass

class ParsedData(BaseModel):
    face: bytes
    traits: Dict[str, List[str]]