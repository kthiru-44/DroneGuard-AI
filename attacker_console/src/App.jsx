import React, { useState } from "react";
import { postAttack, clearAttack } from "./utils/api";
import "./styles.css"; // make sure neon CSS is imported

export default function App() {
  const [activeAttack, setActiveAttack] = useState(null);

  const backend = localStorage.getItem("BACKEND_URL") || "http://127.0.0.1:8000";

  const send = async (mode) => {
    if (!confirm(`Trigger ${mode}?`)) return;

    try {
      const res = await postAttack(backend, { mode });

      // Set banner
      setActiveAttack(mode);

      alert("Attack posted : " + JSON.stringify(res));
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
  console.log("[mDNS] Trying DGBackend.local ...");

  const guess = "http://DGBackend.local:8000";

  try {
    const r = await fetch(guess + "/.well-known/ready", { timeout: 2000 });

    if (r.ok) {
      localStorage.setItem("BACKEND_URL", guess);
      alert("Connected → DGBackend detected via mDNS");
      return;
    }
  } catch (e) {
    console.log("mDNS direct lookup failed, trying fallback scan...");
  }

  // Fallback — old method
  const fallback = "http://127.0.0.1:8000";
  try {
    const r = await fetch(fallback + "/.well-known/ready");
    if (r.ok) {
      localStorage.setItem("BACKEND_URL", fallback);
      alert("Connected locally (fallback mode)");
    }
  } catch (e) {
    alert("No backend found.");
  }
};

  return (
  <div className="console-container">

    <h1>ATTACKER CONSOLE</h1>

    {/* 🔥 ACTIVE ATTACK BANNER */}
    {activeAttack && (
      <div className="active-banner">
        ACTIVE ATTACK: {activeAttack}
      </div>
    )}

    {/* ⭐ CENTERED SEARCH BUTTON */}
    <div className="center-wrapper">
      <button className="btn search-btn big-search" onClick={autoDiscover}>
        Search Drone Console
      </button>
    </div>

    {/* ⭐ ATTACK BUTTON GROUP — CENTERED BELOW */}
    <div className="attack-panel">
      <button className="btn attack-btn" onClick={() => send("GPS_SPOOF")}>GPS Spoof</button>
      <button className="btn attack-btn" onClick={() => send("SPEED_SURGE")}>Speed Surge</button>
      <button className="btn attack-btn" onClick={() => send("DEST_HIJACK")}>Dest Hijack</button>
      <button className="btn attack-btn" onClick={() => send("YAW_SPIKE")}>Yaw Spike</button>
      <button className="btn attack-btn" onClick={() => send("SLOW_DRIFT")}>Slow Drift</button>

      <button className="btn clear-btn" onClick={clearAll}>Clear</button>
    </div>

  </div>
  );
}
