from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.attack_router import attack_router
from .routers.telemetry_router import telemetry_router
from .routers.failsafe_router import failsafe_router

from .websocket_handlers.ws_pi import router as ws_pi_router
from .websocket_handlers.ws_frontend import router as ws_frontend_router

app = FastAPI(title="DroneGuard AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(attack_router)
app.include_router(telemetry_router)
app.include_router(failsafe_router)

app.include_router(ws_pi_router)
app.include_router(ws_frontend_router)
