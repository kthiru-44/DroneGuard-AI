import React from "react";

export default function StatusBar({ status, telemetryCount }){
  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className={`px-3 py-1 rounded-lg text-sm font-semibold ${status==="SAFE" ? "bg-emerald-100 text-emerald-700" : "bg-rose-50 text-rose-700"}`}>
          {status}
        </div>
        <div className="text-xs text-slate-500">System status</div>
      </div>
      <div className="text-sm text-slate-600">Points: <span className="font-medium">{telemetryCount}</span></div>
    </div>
  );
}
