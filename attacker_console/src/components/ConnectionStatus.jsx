import React, { useState } from "react";
import { testConnectivity } from "../utils/api";

export default function ConnectionStatus({ backendUrl, onSave, connected, lastSeen, pushLog }) {
  const [searching, setSearching] = useState(false);

  const autoDiscover = async () => {
    setSearching(true);
    const guess = "http://droneguard.local:8000";

    await new Promise((r) => setTimeout(r, 1200)); // animation delay

    try {
      await testConnectivity(guess);
      onSave(guess);
      pushLog({ ts: new Date().toISOString(), type: "info", msg: "Auto-discovery success." });
      alert("DroneGuard Control Center Found!");
    } catch {
      alert("Not found.");
    }
    setSearching(false);
  };

  return (
    <div className="search-container">
      <button
        className="search-btn"
        onClick={autoDiscover}
        disabled={searching}
      >
        {searching ? "Scanning Network..." : "Search Control Center"}
      </button>
    </div>
  );
}
