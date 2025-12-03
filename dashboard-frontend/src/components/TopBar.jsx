import React from "react";
import ConnectionBadge from "./ConnectionBadge";

export default function TopBar() {
  return (
    <div className="flex items-center justify-between px-6 py-3 border-b border-white/6 bg-gradient-to-r from-[#060616] to-[#071226]">
      <div className="flex items-center gap-3">
        <div className="text-2xl font-bold text-neonCyan">DroneGuard AI</div>
        <div className="text-sm text-white/60">Telemetry Intrusion Protection — Track 4</div>
      </div>
      <div className="flex items-center gap-4">
        <ConnectionBadge />
      </div>
    </div>
  );
}
