import logging

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])
logger = logging.getLogger("hekades")


class StatusOut(BaseModel):
    status: str


@router.get("")
def health_check() -> StatusOut:
    logger.info("Health Check Request Received 🤙")
    return StatusOut(status="ok")
