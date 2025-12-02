import React from "react";

export default function IMUGauge({ telemetry }) {
  const last = telemetry[telemetry.length - 1];
  if (!last) return <div className="text-sm text-slate-500">No IMU yet</div>;
  return (
    <div className="mt-2 space-y-1 text-sm text-slate-700">
      <div><strong>Roll:</strong> {last.roll?.toFixed(2)}</div>
      <div><strong>Pitch:</strong> {last.pitch?.toFixed(2)}</div>
      <div><strong>Yaw:</strong> {last.yaw?.toFixed(2)}</div>
      <div className="mt-2 text-xs text-slate-500">Battery: {last.battery ?? "—"}%</div>
    </div>
  );
}
