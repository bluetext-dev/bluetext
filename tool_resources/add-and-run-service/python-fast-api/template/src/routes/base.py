from fastapi import APIRouter

from utils import log

logger = log.get_logger(__name__)
router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Hello World"}
