# main.py - assemble the FastAPI app
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json

from .config import HOST, PORT, ALLOW_REMOTE_ATTACKS
from .state.telemetry_buffer import TelemetryBuffer
from .state.failsafe_state import FailsafeState

from .websocket_handlers.ws_pi import handle_pi_ws
from .websocket_handlers.ws_frontend import handle_frontend_ws

from .routers import attack_router, failsafe_router, discovery_router

from zeroconf import ServiceInfo, Zeroconf
import socket
import threading

app = FastAPI(title="DroneGuard Local Demo")

# CORS only for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# shared state
app.state.telemetry_buffer = TelemetryBuffer()
app.state.failsafe_state = FailsafeState()
app.state.front_clients = set()

# include routers
app.include_router(attack_router.router)
app.include_router(failsafe_router.router)
app.include_router(discovery_router.router)

@app.websocket("/ws/pi")
async def ws_pi_endpoint(websocket: WebSocket):
    await handle_pi_ws(websocket, {
        "telemetry_buffer": app.state.telemetry_buffer,
        "front_clients": app.state.front_clients,
        "failsafe_state": app.state.failsafe_state
    })

@app.websocket("/ws/frontend")
async def ws_frontend_endpoint(websocket: WebSocket):
    await handle_frontend_ws(websocket, {
        "telemetry_buffer": app.state.telemetry_buffer,
        "front_clients": app.state.front_clients,
        "failsafe_state": app.state.failsafe_state
    })

# mDNS advertisement (optional local-only)
def advertise_mdns():
    try:
        zc = Zeroconf()
        hostname = socket.gethostname() + ".local."
        addr = socket.inet_aton("127.0.0.1")  # advertise localhost for demo
        info = ServiceInfo(
            "_http._tcp.local.",
            "DroneGuard Local Demo._http._tcp.local.",
            addresses=[addr],
            port=PORT,
            properties={},
            server="droneguard.local."
        )
        zc.register_service(info)
        print("[mDNS] advertised droneguard.local -> 127.0.0.1")
        return zc
    except Exception as e:
        print("mDNS advertise failed:", e)
        return None

@app.on_event("startup")
def startup_event():
    # advertise mDNS locally (maps to localhost in this safe demo)
    advert = advertise_mdns()
    app.state._mdns = advert

@app.on_event("shutdown")
def shutdown_event():
    try:
        if getattr(app.state, "_mdns", None):
            app.state._mdns.close()
    except Exception:
        pass

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False)
