import React from "react";
import { useTelemetry } from "../hooks/useTelemetry";

export default function Alerts() {
  const { alerts } = useTelemetry();
  return (
    <div className="card">
      <h3 className="text-lg neon font-semibold mb-3">Alerts Feed</h3>
      <div style={{ maxHeight: "70vh", overflow: "auto" }}>
        {alerts.length === 0 && <div className="text-slate-400">No alerts</div>}
        {alerts.map((a, i) => (
          <div key={i} className="mb-3 p-3 border rounded border-slate-800">
            <div className="font-bold neon">{a.type}</div>
            <div className="text-xs text-slate-300 mt-1">{JSON.stringify(a.detail || a, null, 2)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
