from pydantic import BaseModel
from typing import Dict, List
import aiohttp


class VideoMessage(BaseModel):
    video: str


class PersonInformation(BaseModel):
    traits: Dict[str, List[str]]


class VideoReqResp(BaseModel):
    matches: List[List[Dict]]


async def get_matches_for_user(user: List[float]) -> List[PersonInformation]:
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost/api/core/recvec", json={'face': user}) as resp:
            js = await resp.json()
            if resp.status != 200:
                raise RuntimeError

            return js
