from fastapi import APIRouter
from utils.data import FaceAddRequest

router = APIRouter()


@router.post("/addface/")
def addface(req: FaceAddRequest):
    pass
