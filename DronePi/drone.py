#!/usr/bin/env python3
"""
drone.py - Raspberry Pi demo drone telemetry generator (extended)

Adds:
 - route_override / dest_hijack / teleport_dest injection modes
 - injection_detail included in WS messages for frontend clarity
 - posts diagnostic event to /pi/event on auto-failsafe
 - hybrid auto-failsafe (Option C) preserved
 - mDNS-friendly backend hostnames allowed (droneguard.local)

Run:
    pip install aiohttp websockets
    python3 drone.py --host http://127.0.0.1:8000 --ws ws://127.0.0.1:8000/ws/pi
    or
    python3 drone.py --host http://droneguard.local:8000 --ws ws://droneguard.local:8000/ws/pi
"""

import argparse
import asyncio
import json
import math
import random
import time
from typing import List, Tuple, Optional

import aiohttp
import websockets

# ---------------------------
# Configuration / constants
# ---------------------------
DEFAULT_BACKEND_HOST = "http://127.0.0.1:8000"
DEFAULT_WS_URL = "ws://127.0.0.1:8000/ws/pi"

# polling intervals
ATTACK_POLL_INTERVAL = 1.0     # seconds
FAILSAFE_POLL_INTERVAL = 0.8   # seconds
TELEMETRY_INTERVAL = 0.25      # seconds (send rate)

# flight params
CRUISE_SPEED_MPS = 3.0         # base speed (m/s)
ALTITUDE_M = 40.0              # fixed altitude for demo
BATTERY_DRAIN_PER_SEC = 0.0005

# injection defaults (used if attacker details can't be fetched)
DEFAULT_INJECTION = {
    "mode": "jump",    # jump, speed, heading, gps_drift, route_override, teleport_dest
    "mag": 30.0,       # meters (jump) or multiplier (speed) or degrees (heading)
    "style": "sudden", # sudden or smooth
    "dur": 8           # seconds
}

# hybrid failsafe thresholds (Option C)
JUMP_THRESHOLD_M = 20.0        # if jump injection magnitude > this -> auto failsafe
SPEED_MULTIPLIER_THRESHOLD = 3.0
HEADING_SHIFT_THRESHOLD = 90.0

# example flight path (near Bengaluru, adjust as needed)
WAYPOINTS = [
    (12.9718915, 77.6411545),
    (12.9725, 77.6420),
    (12.9731, 77.6399),
    (12.9717, 77.6385),
    (12.9710, 77.6396)
]

# ---------------------------
# Utilities
# ---------------------------


def now_s() -> float:
    return time.time()


def haversine_m(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Return distance in meters between two lat/lon points."""
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    R = 6371000.0
    a = math.sin(dlat / 2.0) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def bearing_deg(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Return bearing from p1 to p2 in degrees 0-360"""
    lat1, lon1 = math.radians(p1[0]), math.radians(p1[1])
    lat2, lon2 = math.radians(p2[0]), math.radians(p2[1])
    dlon = lon2 - lon1
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    br = math.degrees(math.atan2(x, y))
    return (br + 360.0) % 360.0


def dest_point(p: Tuple[float, float], bearing_deg_: float, distance_m: float) -> Tuple[float, float]:
    """Compute destination point from p along bearing by distance in meters."""
    R = 6371000.0
    lat1 = math.radians(p[0])
    lon1 = math.radians(p[1])
    br = math.radians(bearing_deg_)
    d = distance_m / R
    lat2 = math.asin(math.sin(lat1) * math.cos(d) + math.cos(lat1) * math.sin(d) * math.cos(br))
    lon2 = lon1 + math.atan2(math.sin(br) * math.sin(d) * math.cos(lat1), math.cos(d) - math.sin(lat1) * math.sin(lat2))
    return (math.degrees(lat2), math.degrees(lon2))


# ---------------------------
# Drone-state / Flight generator
# ---------------------------


class FlightGenerator:
    """
    Smoothly walks through waypoints and produces telemetry samples.
    Responsible for interpolation, velocity, yaw, roll, pitch.
    """

    def __init__(self, waypoints: List[Tuple[float, float]], cruise_speed=CRUISE_SPEED_MPS):
        self.waypoints = waypoints[:]
        if len(self.waypoints) < 2:
            raise ValueError("Need >=2 waypoints")
        self.cruise_speed = cruise_speed
        self.index = 0  # current target waypoint idx
        self.pos = self.waypoints[0]
        self.prev_time = now_s()
        self.vx = 0.0
        self.vy = 0.0
        self.speed = 0.0
        self.yaw = 0.0
        self.roll = 0.0
        self.pitch = 0.0
        self.battery = 1.0
        self.source = "normal"

        # route override state
        self.override_waypoints: Optional[List[Tuple[float, float]]] = None
        self.override_index = 0

    def step(self, dt: float, override_speed: Optional[float] = None) -> dict:
        """
        Advance position by dt seconds.
        If override_speed provided (m/s) use it (e.g. for speed injection).
        """
        active_waypoints = self.override_waypoints if self.override_waypoints else self.waypoints
        idx = self.override_index if self.override_waypoints else self.index
        target = active_waypoints[(idx + 1) % len(active_waypoints)]
        dist = haversine_m(self.pos, target)
        speed = override_speed if override_speed is not None else self.cruise_speed
        travel = speed * dt

        # if we can reach (or pass) target in this step, snap and advance
        if travel >= dist and dist > 0:
            new_pos = target
            if self.override_waypoints:
                self.override_index = (self.override_index + 1) % len(self.override_waypoints)
            else:
                self.index = (self.index + 1) % len(self.waypoints)
        elif dist == 0:
            new_pos = self.pos
        else:
            br = bearing_deg(self.pos, target)
            new_pos = dest_point(self.pos, br, travel)

        # compute velocities approximate (vx east, vy north in m/s)
        dy = (new_pos[0] - self.pos[0]) * 111_000.0  # lat degrees to meters approx
        dx = (new_pos[1] - self.pos[1]) * (111_000.0 * math.cos(math.radians(self.pos[0])))
        vx = dx / dt if dt > 0 else 0.0
        vy = dy / dt if dt > 0 else 0.0
        speed_now = math.hypot(vx, vy)

        # yaw = bearing of velocity if speed non-zero else keep old yaw
        if speed_now > 0.01:
            yaw = (math.degrees(math.atan2(vx, vy)) + 360) % 360
        else:
            yaw = self.yaw

        # small pseudo-random roll/pitch fluctuations
        roll = math.sin(now_s() * 0.5 + random.random()) * 5.0
        pitch = math.cos(now_s() * 0.4 + random.random()) * 3.0

        # battery drain
        self.battery = max(0.0, self.battery - BATTERY_DRAIN_PER_SEC * dt)

        # update internal state
        self.pos = new_pos
        self.vx = vx
        self.vy = vy
        self.speed = speed_now
        self.yaw = yaw
        self.roll = roll
        self.pitch = pitch

        pkt = {
            "time": now_s(),
            "gps_lat": float(self.pos[0]),
            "gps_lon": float(self.pos[1]),
            "alt": ALTITUDE_M,
            "vx": float(self.vx),
            "vy": float(self.vy),
            "speed": float(self.speed),
            "yaw": float(self.yaw),
            "roll": float(self.roll),
            "pitch": float(self.pitch),
            "battery": float(self.battery),
            "source": self.source,
        }
        return pkt

    def set_route_override(self, waypoints: List[Tuple[float, float]]):
        if not waypoints:
            self.override_waypoints = None
            self.override_index = 0
            return
        self.override_waypoints = waypoints[:]
        self.override_index = 0
        print("[FLIGHT] route override set:", self.override_waypoints)

    def clear_route_override(self):
        if self.override_waypoints:
            print("[FLIGHT] clearing route override")
        self.override_waypoints = None
        self.override_index = 0


# ---------------------------
# Injection behaviours
# ---------------------------


class Injection:
    """Manages currently active injection (if any)."""

    def __init__(self):
        self.active = False
        self.mode = None
        self.mag = None
        self.style = None
        self.dur = None
        self.started_at = None
        self.raw = None  # raw attack payload (for reporting)
        # For smooth jump tracking
        self.jump_origin = None
        # For route override storage
        self.route_waypoints = None

    def start(self, params: dict):
        self.active = True
        self.mode = params.get("mode", DEFAULT_INJECTION["mode"])
        self.mag = float(params.get("mag", DEFAULT_INJECTION["mag"]))
        self.style = params.get("style", DEFAULT_INJECTION["style"])
        self.dur = int(params.get("dur", DEFAULT_INJECTION["dur"]))
        self.started_at = now_s()
        self.raw = params.copy() if isinstance(params, dict) else {"raw": params}
        self.jump_origin = None
        self.route_waypoints = None
        # extract route override if attacker sent explicit coords/list
        if "target_lat" in params and "target_lon" in params:
            try:
                lat = float(params["target_lat"])
                lon = float(params["target_lon"])
                self.route_waypoints = [(lat, lon)]
            except Exception:
                self.route_waypoints = None
        if "waypoints" in params and isinstance(params["waypoints"], list) and params["waypoints"]:
            # expect list of [lat,lon] pairs or dicts
            pts = []
            for w in params["waypoints"]:
                if isinstance(w, (list, tuple)) and len(w) >= 2:
                    pts.append((float(w[0]), float(w[1])))
                elif isinstance(w, dict) and "lat" in w and "lon" in w:
                    pts.append((float(w["lat"]), float(w["lon"])))
            if pts:
                self.route_waypoints = pts
        print(f"[INJECTION] start: mode={self.mode} mag={self.mag} style={self.style} dur={self.dur} raw_id={self.raw.get('id') if isinstance(self.raw, dict) else None}")

    def is_expired(self):
        if not self.active:
            return True
        return (now_s() - self.started_at) > max(0.5, self.dur)

    def stop(self):
        if self.active:
            print("[INJECTION] stopped")
        self.active = False
        self.mode = None
        self.mag = None
        self.style = None
        self.dur = None
        self.started_at = None
        self.raw = None
        self.jump_origin = None
        self.route_waypoints = None


async def apply_injection_to_pkt(pkt: dict, fg: FlightGenerator, inj: Injection):
    """
    Modify pkt in-place according to injection parameters.
    Modes:
     - jump: teleport the GPS coordinate by 'mag' meters (sudden) or over duration (smooth)
     - speed: increase speed by multiplier 'mag' (e.g. 2.0 doubles speed)
     - heading: force yaw to yaw + mag degrees
     - gps_drift: slowly drift position by mag meters per second (vector random)
     - route_override / dest_hijack: temporarily override flight route to attacker coords (inj.raw may contain coords)
     - teleport_dest: immediate teleport to exact attacker-provided lat/lon (target_lat/target_lon)
    """
    if not inj.active:
        return pkt

    elapsed = now_s() - inj.started_at
    remaining = max(0.0, inj.dur - elapsed)

    # route override handling: if attacker provided explicit target coords or waypoints
    if inj.route_waypoints:
        # set flight generator route override if not set already
        if fg.override_waypoints is None:
            fg.set_route_override(inj.route_waypoints)
        # mark injected source and don't change values further for other modes below
        pkt["source"] = "injected"
        return pkt

    if inj.mode == "jump":
        if inj.style == "sudden":
            # jump immediately (only once)
            if elapsed < TELEMETRY_INTERVAL * 1.5:
                # choose random bearing
                b = random.uniform(0, 360)
                newpos = dest_point((pkt["gps_lat"], pkt["gps_lon"]), b, inj.mag)
                pkt["gps_lat"], pkt["gps_lon"] = newpos
                pkt["source"] = "injected"
                pkt["vx"], pkt["vy"] = 0.0, 0.0
                pkt["speed"] = 0.0
        else:
            # smooth: interpolate position along a small circle for the duration
            if inj.jump_origin is None:
                inj.jump_origin = (pkt["gps_lat"], pkt["gps_lon"])
            frac = min(1.0, elapsed / max(0.001, inj.dur))
            b = (elapsed * 150.0) % 360
            offset = inj.mag * frac
            newpos = dest_point(inj.jump_origin, b, offset)
            pkt["gps_lat"], pkt["gps_lon"] = newpos
            pkt["source"] = "injected"

    elif inj.mode == "speed":
        multiplier = inj.mag if inj.mag and inj.mag > 0 else 1.0
        pkt["speed"] = float(pkt.get("speed", 0.0) * multiplier)
        pkt["vx"] = float(pkt.get("vx", 0.0) * multiplier)
        pkt["vy"] = float(pkt.get("vy", 0.0) * multiplier)
        pkt["source"] = "injected"

    elif inj.mode == "heading":
        pkt["yaw"] = (pkt.get("yaw", 0.0) + inj.mag) % 360.0
        pkt["source"] = "injected"

    elif inj.mode == "gps_drift":
        b = random.uniform(0, 360)
        drift = inj.mag * TELEMETRY_INTERVAL
        newpos = dest_point((pkt["gps_lat"], pkt["gps_lon"]), b, drift)
        pkt["gps_lat"], pkt["gps_lon"] = newpos
        pkt["source"] = "injected"

    elif inj.mode in ("route_override", "dest_hijack"):
        # attacker may supply explicit lat/lon in inj.raw
        if inj.raw:
            tlat = inj.raw.get("target_lat") or inj.raw.get("lat")
            tlon = inj.raw.get("target_lon") or inj.raw.get("lon")
            if tlat is not None and tlon is not None:
                try:
                    lat = float(tlat)
                    lon = float(tlon)
                    # immediate steering: set flight generator override to single target
                    fg.set_route_override([(lat, lon)])
                    pkt["source"] = "injected"
                except Exception:
                    pass
        else:
            pkt["source"] = "injected"

    elif inj.mode == "teleport_dest":
        # immediate teleport to exact coords if provided
        if inj.raw and ("target_lat" in inj.raw and "target_lon" in inj.raw):
            try:
                lat = float(inj.raw["target_lat"])
                lon = float(inj.raw["target_lon"])
                pkt["gps_lat"], pkt["gps_lon"] = lat, lon
                pkt["vx"], pkt["vy"], pkt["speed"] = 0.0, 0.0, 0.0
                pkt["source"] = "injected"
            except Exception:
                pass

    else:
        pkt["source"] = "injected"

    return pkt


# ---------------------------
# Network helpers
# ---------------------------


class BackendClient:
    def __init__(self, backend_host: str, ws_url: str):
        # Accept backend_host like http://droneguard.local:8000 (mDNS friendly),
        # or http://127.0.0.1:8000
        self.backend_host = backend_host.rstrip("/")
        self.ws_url = ws_url
        self.session = aiohttp.ClientSession()
        self.attack_state = False
        self.failsafe_state = {"active": False}
        self.latest_attacks = []
        self.attempted_attack_fetch = False

    async def close(self):
        await self.session.close()

    # -------------------
    # Attack state APIs
    # -------------------
    async def get_attack_state(self) -> bool:
        url = f"{self.backend_host}/pi/attack-state"
        try:
            async with self.session.get(url, timeout=2.0) as r:
                if r.status == 200:
                    jd = await r.json()
                    val = bool(jd.get("active", False))
                    self.attack_state = val
                    return val
        except Exception:
            return self.attack_state
        return self.attack_state

    async def fetch_latest_attack(self) -> Optional[dict]:
        url = f"{self.backend_host}/attack/list"
        try:
            async with self.session.get(url, timeout=2.0) as r:
                if r.status == 200:
                    jd = await r.json()
                    if isinstance(jd, list) and jd:
                        return jd[-1]
                    if isinstance(jd, dict) and "attacks" in jd and isinstance(jd["attacks"], list) and jd["attacks"]:
                        return jd["attacks"][-1]
                    return jd
        except Exception:
            return None

    async def try_fetch_attack_details(self) -> Optional[dict]:
        det = await self.fetch_latest_attack()
        if det:
            return det
        candidates = ["/attack", "/attacks", "/pi/attacks"]
        for ep in candidates:
            url = f"{self.backend_host}{ep}"
            try:
                async with self.session.get(url, timeout=2.0) as r:
                    if r.status == 200:
                        jd = await r.json()
                        if isinstance(jd, list) and jd:
                            return jd[-1]
                        if isinstance(jd, dict):
                            if "attacks" in jd and isinstance(jd["attacks"], list) and jd["attacks"]:
                                return jd["attacks"][-1]
                            return jd
            except Exception:
                continue
        return None

    # -------------------
    # Failsafe APIs
    # -------------------
    async def get_failsafe_state(self) -> dict:
        url = f"{self.backend_host}/failsafe/state"
        try:
            async with self.session.get(url, timeout=2.0) as r:
                if r.status == 200:
                    jd = await r.json()
                    self.failsafe_state = jd
                    return jd
        except Exception:
            return self.failsafe_state
        return self.failsafe_state

    async def post_activate_failsafe(self, reason: str = "drone_auto"):
        url = f"{self.backend_host}/failsafe/activate"
        payload = {"reason": reason}
        try:
            async with self.session.post(url, json=payload, timeout=2.0) as r:
                if r.status in (200, 201):
                    jd = await r.json()
                    # common routers return {"status":"ok","failsafe":fs}
                    if isinstance(jd, dict) and "failsafe" in jd:
                        self.failsafe_state = jd["failsafe"]
                    else:
                        self.failsafe_state = jd
                    return jd
                else:
                    try:
                        return await r.json()
                    except Exception:
                        return {"status": "error", "code": r.status}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    # diagnostic event (best-effort)
    async def post_pi_event(self, event: dict):
        url = f"{self.backend_host}/pi/event"
        try:
            async with self.session.post(url, json=event, timeout=2.0) as r:
                try:
                    return await r.json()
                except Exception:
                    return {"status": "ok", "code": r.status}
        except Exception as e:
            # backend may not provide endpoint; ignore
            return {"status": "error", "error": str(e)}

    # convenience wrapper - generic post
    async def post_event(self, path: str, data: dict):
        url = f"{self.backend_host}{path}"
        try:
            async with self.session.post(url, json=data, timeout=2.0) as r:
                try:
                    return await r.json()
                except Exception:
                    return {"status": "ok", "code": r.status}
        except Exception as e:
            return {"status": "error", "error": str(e)}


# ---------------------------
# Drone intelligence: auto-failsafe decision
# ---------------------------


def should_auto_failsafe_on_injection(inj: Injection, pkt_before: dict, pkt_after: dict) -> Optional[str]:
    """
    Heuristic hybrid rules (Option C):
      - sudden jump mag > JUMP_THRESHOLD_M -> trigger
      - speed multiplier > SPEED_MULTIPLIER_THRESHOLD -> trigger
      - heading shift > HEADING_SHIFT_THRESHOLD -> trigger
      - teleport to far coordinate -> trigger
    Returns reason string if triggering, else None.
    """
    if not inj.active:
        return None

    mode = (inj.mode or "").lower()
    mag = inj.mag or 0.0

    try:
        if mode == "jump":
            before = (float(pkt_before["gps_lat"]), float(pkt_before["gps_lon"]))
            after = (float(pkt_after["gps_lat"]), float(pkt_after["gps_lon"]))
            d = haversine_m(before, after)
            if d >= JUMP_THRESHOLD_M or mag >= JUMP_THRESHOLD_M:
                return f"AUTO_FAILSAFE_JUMP_{int(d)}m"
        elif mode == "speed":
            if mag >= SPEED_MULTIPLIER_THRESHOLD:
                return f"AUTO_FAILSAFE_SPEED_x{mag}"
        elif mode == "heading":
            if abs(float(mag)) >= HEADING_SHIFT_THRESHOLD:
                return f"AUTO_FAILSAFE_HEADING_{int(abs(mag))}deg"
        elif mode in ("route_override", "dest_hijack", "teleport_dest"):
            # if attacker provided explicit target and it's far from current pos
            try:
                if inj.raw:
                    tlat = inj.raw.get("target_lat") or inj.raw.get("lat")
                    tlon = inj.raw.get("target_lon") or inj.raw.get("lon")
                    if tlat is not None and tlon is not None:
                        before = (float(pkt_before["gps_lat"]), float(pkt_before["gps_lon"]))
                        after = (float(tlat), float(tlon))
                        d = haversine_m(before, after)
                        if d >= JUMP_THRESHOLD_M:
                            return f"AUTO_FAILSAFE_HIJACK_{int(d)}m"
            except Exception:
                pass
        elif mode == "gps_drift":
            if mag >= JUMP_THRESHOLD_M / 2.0:
                return f"AUTO_FAILSAFE_DRIFT_{mag}"
    except Exception:
        return None

    return None


# ---------------------------
# Main drone loop + websocket client
# ---------------------------


async def drone_loop(ws, fgen: FlightGenerator, client: BackendClient):
    inj = Injection()
    last_attack_check = 0.0
    last_failsafe_check = 0.0
    last_send = 0.0
    send_interval = TELEMETRY_INTERVAL
    prev_time = now_s()

    while True:
        try:
            # time step
            t0 = now_s()
            dt = max(1e-6, t0 - prev_time)
            prev_time = t0

            # poll attack state periodically
            if t0 - last_attack_check >= ATTACK_POLL_INTERVAL:
                active = await client.get_attack_state()
                last_attack_check = t0
                if active and not inj.active:
                    # try to fetch attack details; if none, use default
                    details = await client.try_fetch_attack_details()
                    if details:
                        inj.start(details)
                        # if injection contained route override, apply to flight generator immediately
                        if inj.route_waypoints:
                            fgen.set_route_override(inj.route_waypoints)
                    else:
                        inj.start(DEFAULT_INJECTION)
                elif not active and inj.active:
                    # clear injection and any route override if present
                    inj.stop()
                    fgen.clear_route_override()

            # poll failsafe state
            if t0 - last_failsafe_check >= FAILSAFE_POLL_INTERVAL:
                fs = await client.get_failsafe_state()
                last_failsafe_check = t0
                if fs.get("active", False):
                    # backend says failsafe active -> freeze
                    if inj.active:
                        inj.stop()
                    fgen.source = "failsafe"
                else:
                    if fgen.source == "failsafe":
                        fgen.source = "normal"

            # generate telemetry sample
            if fgen.source == "failsafe":
                # freeze packet from current state
                pkt = {
                    "time": now_s(),
                    "gps_lat": float(fgen.pos[0]),
                    "gps_lon": float(fgen.pos[1]),
                    "alt": ALTITUDE_M,
                    "vx": 0.0,
                    "vy": 0.0,
                    "speed": 0.0,
                    "yaw": float(fgen.yaw),
                    "roll": float(fgen.roll),
                    "pitch": float(fgen.pitch),
                    "battery": float(fgen.battery),
                    "source": "failsafe",
                }
                injection_report = None
            else:
                # normal flight step
                pkt_before = {
                    "gps_lat": float(fgen.pos[0]),
                    "gps_lon": float(fgen.pos[1]),
                    "speed": float(fgen.speed),
                    "yaw": float(fgen.yaw)
                }
                pkt = fgen.step(dt)

                injection_report = None
                if inj.active:
                    # inject and build injection_detail for reporting
                    pkt_after = await apply_injection_to_pkt(pkt.copy(), fgen, inj)
                    # create short human-friendly report
                    inj_report = {
                        "mode": inj.mode,
                        "mag": inj.mag,
                        "style": inj.style,
                        "dur": inj.dur,
                        "raw": inj.raw
                    }
                    injection_report = inj_report

                    # decide if injection should auto-failsafe
                    reason = should_auto_failsafe_on_injection(inj, pkt_before, pkt_after)
                    if reason:
                        pkt = pkt_after
                        pkt["source"] = "injected"
                        fgen.source = "injected"
                        print(f"[AUTO FAILSAFE] local decision: {reason} -> requesting backend activate")
                        # call backend to activate failsafe
                        resp = await client.post_activate_failsafe(reason=reason)
                        # post diagnostic event to backend
                        diag = {
                            "event": "auto_failsafe",
                            "reason": reason,
                            "attack": inj.raw,
                            "timestamp": now_s()
                        }
                        try:
                            await client.post_pi_event(diag)
                        except Exception:
                            pass
                        # immediately set local freeze (optimistic)
                        fgen.source = "failsafe"
                        inj.stop()
                        # clear route override if present (because now frozen)
                        fgen.clear_route_override()
                    else:
                        # apply injection normally
                        pkt = pkt_after
                        pkt["source"] = "injected"
                        fgen.source = "injected"

                        if inj.is_expired():
                            inj.stop()
                            if fgen.source != "failsafe":
                                pkt["source"] = "normal"
                                fgen.source = "normal"
                                # clear any route override set by injection
                                fgen.clear_route_override()
                else:
                    pkt["source"] = "normal"

            # ensure numeric types consistent
            pkt["time"] = float(pkt.get("time", now_s()))
            pkt["gps_lat"] = float(pkt.get("gps_lat", 0.0))
            pkt["gps_lon"] = float(pkt.get("gps_lon", 0.0))
            pkt["vx"] = float(pkt.get("vx", 0.0))
            pkt["vy"] = float(pkt.get("vy", 0.0))
            pkt["speed"] = float(pkt.get("speed", 0.0))
            pkt["yaw"] = float(pkt.get("yaw", 0.0))
            pkt["roll"] = float(pkt.get("roll", 0.0))
            pkt["pitch"] = float(pkt.get("pitch", 0.0))
            pkt["battery"] = float(pkt.get("battery", 0.0))
            pkt["source"] = pkt.get("source", fgen.source)

            # Build WS envelope including injection_detail so frontend can show it
            ws_msg = {
                "type": "telemetry",
                "payload": pkt,
                "injection_detail": injection_report  # can be None or dict
            }

            # send telemetry over WS (backend expects {"payload": pkt} previously) - keep compatibility: still send payload-only too
            now_send = now_s()
            if now_send - last_send >= send_interval:
                last_send = now_send
                try:
                    # send modern envelope
                    await ws.send(json.dumps(ws_msg))
                except (websockets.exceptions.ConnectionClosed, ConnectionResetError) as e:
                    print("[WS] connection closed while sending:", e)
                    raise

            await asyncio.sleep(0.001)

        except Exception as e:
            print("[drone_loop] exception:", e)
            raise


async def ws_main_loop(backend_host: str, ws_url: str):
    client = BackendClient(backend_host, ws_url)
    fgen = FlightGenerator(WAYPOINTS, cruise_speed=CRUISE_SPEED_MPS)

    try:
        while True:
            try:
                print(f"[WS] Connecting to backend WS: {ws_url}")
                async with websockets.connect(ws_url, ping_interval=10, ping_timeout=5) as ws:
                    print("[WS] Connected to backend!")
                    try:
                        await ws.send(json.dumps({"payload": {"hello": "drone_pi", "time": now_s()}}))
                    except Exception:
                        pass

                    await drone_loop(ws, fgen, client)

            except (websockets.exceptions.InvalidURI, websockets.exceptions.InvalidHandshake) as e:
                print("[WS] WebSocket error:", e)
                await asyncio.sleep(2.0)
            except (ConnectionRefusedError, OSError) as e:
                print("[WS] Connection refused / OS error:", e)
                await asyncio.sleep(2.0)
            except Exception as e:
                print("[WS] Unexpected error, will reconnect in 1s:", e)
                await asyncio.sleep(1.0)
    finally:
        await client.close()


# ---------------------------
# CLI / entrypoint
# ---------------------------

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default=DEFAULT_BACKEND_HOST, help="Backend HTTP host (http://...) - mDNS hostnames allowed (droneguard.local)")
    p.add_argument("--ws", default=DEFAULT_WS_URL, help="Backend websocket url (ws://...) - mDNS hostnames allowed")
    return p.parse_args()


def main():
    args = parse_args()
    backend_host = args.host
    ws_url = args.ws
    try:
        asyncio.run(ws_main_loop(backend_host, ws_url))
    except KeyboardInterrupt:
        print("Terminated by user")


if __name__ == "__main__":
    main()
