import React from "react";

export default function AlertsPanel({ alerts = [], compact=false }){
  if (!alerts.length) {
    return <div className="text-sm text-slate-500">No alerts yet.</div>;
  }
  return (
    <div className="space-y-2">
      {alerts.slice(0, 10).map((a, i) => (
        <div key={i} className="p-3 rounded-lg bg-rose-50 border-l-4 border-rose-300">
          <div className="text-sm font-semibold text-rose-700">{a.type ?? "Anomaly"}</div>
          <div className="text-xs text-slate-600 mt-1">{a.reason ?? ""}</div>
          {a.distance_jump && <div className="text-xs text-slate-500 mt-1">Jump: {Math.round(a.distance_jump)} m</div>}
        </div>
      ))}
    </div>
  );
}
