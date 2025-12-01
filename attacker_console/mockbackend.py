# mock_backend.py (demo-only, safe)
from fastapi import FastAPI
from pydantic import BaseModel
import time

app = FastAPI()

state = {"attacks": []}

@app.get("/pi/attack-state")
def attack_state():
    return {"status":"ok","time": time.time(), "active": bool(state["attacks"])}

@app.post("/attack")
def attack(mode: str = None, mag: float = 1.0, style: str = "sudden", dur: int = 10):
    entry = {"mode": mode, "mag": mag, "style": style, "dur": dur, "ts": time.time()}
    state["attacks"].append(entry)
    return {"status":"ok","received":entry}

@app.post("/attack/clear")
def clear_attack():
    state["attacks"].clear()
    return {"status":"ok","cleared":True}
