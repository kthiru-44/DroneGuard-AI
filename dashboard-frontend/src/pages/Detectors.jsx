import React from "react";
import NeonCard from "../components/NeonCard";
import { useTelemetry } from "../hooks/useTelemetry";

export default function Detectors() {
  const { alerts } = useTelemetry();
  const grouped = alerts.reduce((acc, a) => {
    const k = a.type || "unknown";
    acc[k] = acc[k] || [];
    acc[k].push(a);
    return acc;
  }, {});

  return (
    <div className="grid grid-cols-2 gap-6">
      <NeonCard>
        <h3 className="text-neonCyan">Detector Rules</h3>
        <ul className="mt-3 text-white/70">
          <li>- Physics check: impossibly fast jumps</li>
          <li>- GPS spoof: sudden location jumps inconsistent with IMU</li>
          <li>- IMU mismatch: big difference yaw vs heading</li>
        </ul>
      </NeonCard>

      <NeonCard>
        <h3 className="text-neonCyan">Live Outputs</h3>
        {Object.entries(grouped).length === 0 && <div className="text-white/60">No alerts</div>}
        {Object.entries(grouped).map(([type, arr]) => (
          <div key={type} className="mt-3">
            <div className="font-bold">{type} <span className="text-white/60">({arr.length})</span></div>
            <div className="text-xs text-white/60 mt-2">{JSON.stringify(arr[0].detail || arr[0], null, 2)}</div>
          </div>
        ))}
      </NeonCard>
    </div>
  );
}
