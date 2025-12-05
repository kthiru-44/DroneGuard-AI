# discovery_router.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/.well-known/ready")
async def ready():
    return {"status":"ok", "service": "DroneGuard"}
