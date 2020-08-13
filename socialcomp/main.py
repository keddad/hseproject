from fastapi import FastAPI, HTTPException
from utils import BadID, ParsedData
from parsers.vk import vk
from parsers.ok import ok
import aiohttp
import ujson
import uvicorn
from loguru import logger
from base64 import b85encode

app = FastAPI()

NETWORKS = {
    "VK": vk,
    "OK": ok
}


@app.get("/api/social/generate_204", status_code=204)
def generate_204():
    return


@app.post("/api/parse/{network}/{page_id}")
async def process(network: str, page_id: str):
    if network not in NETWORKS:
        raise HTTPException(status_code=404, detail="Network not supported")

    try:
        data: ParsedData = await NETWORKS[network](page_id)
    except (BadID):
        raise HTTPException(
            status_code=404, detail="No such ID, or unable to parse it due to privacy issues")
    except Exception as e:
        logger.error(f"Internal parser error, {str(e)}")
        raise HTTPException(
            status_code=503, detail=f"Internal parser error, {str(e)}")

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post("http://ff_corecomp:3800/api/core/addface/",
                                json={"face": b85encode(data.face).decode(), "traits": data.traits}) as req:
            if req.status != 200:
                req_json = await req.json()
                raise HTTPException(
                    status_code=503, detail=f"Corecomp error: {req_json['detail']}")


logger.info("Socialcomp up and running")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)  # To debug outside of container
