import React, { useState } from "react";
import { postAttack, clearAttack } from "./utils/api";
import "./styles.css"; // make sure neon CSS is imported

export default function App() {
  const [activeAttack, setActiveAttack] = useState(null);

  const backend = localStorage.getItem("BACKEND_URL") || "http://127.0.0.1:8000";

  const send = async (mode) => {
    if (!confirm(`Trigger ${mode}? This is a local-only demo.`)) return;

    try {
      const res = await postAttack(backend, { mode });

      // Set banner
      setActiveAttack(mode);

      alert("Attack posted (local demo): " + JSON.stringify(res));
    } catch (e) {
      alert("Error: " + e.message);
    }
  };

  const clearAll = async () => {
    if (!confirm("Clear attacks?")) return;

    try {
      await clearAttack(backend);
      setActiveAttack(null); // remove banner
      alert("Cleared");
    } catch (e) {
      alert("Error: " + e.message);
    }
  };

  const autoDiscover = async () => {
    const guess = "http://127.0.0.1:8000";

    try {
      const r = await fetch(guess + "/.well-known/ready");
      if (r.ok) {
        localStorage.setItem("BACKEND_URL", guess);
        alert("Found local control center");
      } else {
        alert("Not found locally");
      }
    } catch (e) {
      alert("Not found locally");
    }
  };

  return (
    <div className="console-container">
      <h1>Attacker Console — Neon Hacker Mode</h1>

      {/* 🔥 ACTIVE ATTACK BANNER */}
      {activeAttack && (
        <div className="active-banner">
          ACTIVE ATTACK: {activeAttack}
        </div>
      )}

      {/* Attack Buttons */}
      <div>
        <button className="btn attack-btn" onClick={() => send("GPS_SPOOF")}>
          GPS Spoof
        </button>

        <button className="btn attack-btn" onClick={() => send("SPEED_SURGE")}>
          Speed Surge
        </button>

        <button className="btn attack-btn" onClick={() => send("DEST_HIJACK")}>
          Dest Hijack
        </button>

        <button className="btn attack-btn" onClick={() => send("YAW_SPIKE")}>
          Yaw Spike
        </button>

        <button className="btn attack-btn" onClick={() => send("SLOW_DRIFT")}>
          Slow Drift
        </button>

        <button className="btn clear-btn" onClick={clearAll}>
          Clear
        </button>
      </div>

      {/* Auto Discover */}
      <button className="btn search-btn" onClick={autoDiscover}>
        Search Control Center (local)
      </button>
    </div>
  );
}
