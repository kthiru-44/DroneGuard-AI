from fastapi import APIRouter
from ..state.failsafe_state import get_failsafe, reset_failsafe

router = APIRouter()

@router.get("/failsafe/state")
def read_failsafe():
    return get_failsafe()

@router.post("/failsafe/reset")
def reset():
    reset_failsafe()
    return {"status": "reset"}

# IMPORTANT: FastAPI uses this name
failsafe_router = router
