# app/websocket_handlers/ws_frontend.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from typing import Set, Dict, Any
import json

router = APIRouter()

_frontend_clients: Set[WebSocket] = set()
_lock = asyncio.Lock()

@router.websocket("/ws/frontend")
async def websocket_frontend_endpoint(ws: WebSocket):
    await ws.accept()
    async with _lock:
        _frontend_clients.add(ws)
    try:
        # keep connection open; frontend doesn't have to send messages
        while True:
            # simply await receive_text to detect disconnects or ping messages
            try:
                await ws.receive_text()
            except Exception:
                break
    except WebSocketDisconnect:
        pass
    finally:
        async with _lock:
            _frontend_clients.discard(ws)

async def broadcast_to_frontend(message: Dict[str, Any]):
    """
    Broadcast a JSON-able object to all connected frontends.
    Will ignore send errors and cleanup dead sockets.
    """
    text = None
    try:
        text = json.dumps(message)
    except Exception:
        text = str(message)
    dead = []
    async with _lock:
        clients = list(_frontend_clients)
    for client in clients:
        try:
            await client.send_text(text)
        except Exception:
            dead.append(client)
    if dead:
        async with _lock:
            for d in dead:
                _frontend_clients.discard(d)
