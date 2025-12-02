from fastapi import APIRouter, WebSocket
import asyncio

router = APIRouter()

# store all connected frontend sockets
connected_frontends = set()

async def broadcast_to_frontend(message: dict):
    """Send telemetry + alerts + failsafe to ALL dashboard clients."""
    dead = []
    for ws in connected_frontends:
        try:
            await ws.send_json(message)
        except:
            dead.append(ws)

    # remove disconnected websockets
    for ws in dead:
        connected_frontends.remove(ws)


@router.websocket("/ws/frontend")
async def ws_frontend(websocket: WebSocket):
    await websocket.accept()
    connected_frontends.add(websocket)

    try:
        while True:
            await websocket.receive_text()  # dashboard never sends anything
    except:
        pass
    finally:
        if websocket in connected_frontends:
            connected_frontends.remove(websocket)
