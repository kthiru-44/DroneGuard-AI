# ws_frontend.py - accepts frontend websocket connections and registers them
import json
from fastapi import WebSocket

async def handle_frontend_ws(websocket: WebSocket, shared):
    await websocket.accept()
    # register
    shared["front_clients"].add(websocket)
    try:
        # keep open until disconnect
        while True:
            msg = await websocket.receive_text()
            # frontend may send control messages in JSON (not required)
            # echo back minimal ack
            try:
                data = json.loads(msg)
                await websocket.send_text(json.dumps({"type":"ack", "payload": data}))
            except Exception:
                await websocket.send_text(json.dumps({"type":"ack", "payload": "ok"}))
    except Exception:
        pass
    finally:
        try:
            shared["front_clients"].remove(websocket)
        except Exception:
            pass
