from fastapi import APIRouter, Request
from src.services.health_service import get_server_health
from src.models.responses import HealthResponse

router = APIRouter(
    prefix="/health",
    tags=["Health"]
)

@router.get("", response_model=HealthResponse)
async def health_check(request: Request):
    return get_server_health(request)
