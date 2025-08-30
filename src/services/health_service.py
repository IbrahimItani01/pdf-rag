from fastapi import Request
from src.models.responses import HealthResponse
def get_server_health(request: Request ) -> HealthResponse:
    return HealthResponse(
        message="Server running",
        version=request.app.version,
        title=request.app.title,
        description=request.app.description
    )