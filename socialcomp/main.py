from fastapi import FastAPI, HTTPException
from utils import BadID, ParsedData
from parsers.vk import vk
import aiohttp
import ujson
from base64 import b85encode

app = FastAPI()

NETWORKS = {
    "VK": vk
}


@app.get("/api/social/generate_204", status_code=204)
def generate_204():
    return


@app.post("/api/parse/{network}/{id}")
def process(network: str, id: str):
    if network not in NETWORKS:
        raise HTTPException(status_code=404, detail="Network not supported")

    try:
        data: ParsedData = await NETWORKS[network](id)
    except BadID:
        raise HTTPException(
            status_code=404, detail="No such ID, or unable to parse it due to privacy issues")
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Internal parser error, {str(e)}")

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post("http://ff_corecomp:3800", json={"face": b85encode(data.face).decode(), "traits": data.trits}) as req:
            if req.status != 200:
                req_json = await req.json()
                raise HTTPException(
            status_code=503, detail=f"Corecomp error: {req_json['detail']}")


