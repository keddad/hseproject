from fastapi import APIRouter
from utils.data import FaceRecRequest, PersonInformation, FaceRecResponce, VecRecRequest

router = APIRouter()


@router.get("/recface/", response_model=FaceRecResponce)
async def recface(req: FaceRecRequest):
    pass


@router.get("/recvec/", response_model=FaceRecResponce)
async def recvec(req: VecRecRequest):
    pass
