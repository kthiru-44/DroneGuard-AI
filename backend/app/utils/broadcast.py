# utils/broadcast.py

from fastapi import WebSocket

# Store frontend websocket connections
frontend_connections: list[WebSocket] = []


async def broadcast_to_frontend(message: dict):
    """Send data to all connected frontend clients."""
    dead = []

    for conn in frontend_connections:
        try:
            await conn.send_json(message)
        except:
            dead.append(conn)

    # Remove closed connections
    for d in dead:
        frontend_connections.remove(d)
