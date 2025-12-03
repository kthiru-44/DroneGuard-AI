# app/main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from .websocket_handlers import ws_pi, ws_frontend
from .api import control

app = FastAPI(title="DroneGuard-AI Backend (demo)")

# allow local dev origins (frontend at localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],  # demo: allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include HTTP control routes
app.include_router(control.router)

# include websocket routers
app.include_router(ws_frontend.router) if hasattr(ws_frontend, "router") else None
app.include_router(ws_pi.router)
