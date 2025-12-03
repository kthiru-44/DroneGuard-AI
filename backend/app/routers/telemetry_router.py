from fastapi import APIRouter
from ..state.telemetry_buffer import get_buffer

telemetry_router = APIRouter(prefix="/telemetry", tags=["Telemetry"])

@telemetry_router.get("/buffer")
def fetch_buffer():
    return get_buffer()
