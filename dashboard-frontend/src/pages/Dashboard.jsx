// src/pages/Dashboard.jsx

import React from "react";
import NeonCard from "../components/NeonCard";
import MiniMap from "../components/MiniMap";
import { useTelemetry } from "../hooks/useTelemetry";

export default function Dashboard() {
  const { telemetry, alerts, failsafe } = useTelemetry();
  const last = telemetry[0];

  return (
    <div className="grid grid-cols-3 gap-6">
      {/* LEFT 2/3 */}
      <section className="col-span-2">
        {/* OVERVIEW CARD */}
        <NeonCard>
          <h3 className="text-lg font-semibold text-neonCyan">Overview</h3>

          <div className="mt-4 grid grid-cols-2 gap-4">
            {/* IMU ------------------------------------------------- */}
            <div>
              <div className="text-sm text-white/60">Live IMU</div>
              <div className="mt-2 text-white">
                <div>Roll: {last?.roll ?? "--"}</div>
                <div>Pitch: {last?.pitch ?? "--"}</div>
                <div>Yaw: {last?.yaw ?? "--"}</div>
                <div>Battery: {last?.raw?.battery ?? "--"}</div>
              </div>
            </div>

            {/* ALERTS ------------------------------------------------- */}
            <div>
              <div className="text-sm text-white/60">Latest Alerts</div>
              <div className="mt-2 text-white/80">
                {alerts.length === 0 ? (
                  "No alerts yet."
                ) : (
                  <ul className="list-disc pl-5 space-y-2">
                    {alerts.slice(0, 6).map((a, i) => (
                      <li key={i}>
                        {a.type} —{" "}
                        {a.detail?.message ??
                          JSON.stringify(a.detail ?? a).slice(0, 40)}
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          </div>
        </NeonCard>

        {/* FLIGHT PATH + MINI MAP ------------------------------------------------- */}
        <div className="mt-6">
          <NeonCard>
            <h4 className="font-semibold text-neonCyan mb-3">Flight Path</h4>

            <div className="h-80 w-full">
              <MiniMap />
            </div>
          </NeonCard>
        </div>
      </section>

      {/* RIGHT SIDEBAR 1/3 */}
      <aside>
        {/* FAILSAFE STATE ------------------------------------------------- */}
        <NeonCard>
          <div className="text-sm">Failsafe</div>
          <div className="mt-2 text-white">
            {failsafe?.active
              ? `Active (${failsafe.reason})`
              : "Inactive"}
          </div>
        </NeonCard>

        {/* CONTROLS ------------------------------------------------- */}
        <div className="mt-4">
          <NeonCard>
            <div className="text-sm">Controls</div>
            <div className="mt-2">
              <button
                className="px-3 py-2 rounded bg-neonPink text-black"
                onClick={() => {
                  // this button only triggers toast unless you wire real API
                  fetch("http://127.0.0.1:8000/failsafe/activate", {
                    method: "POST",
                  })
                    .then((res) => res.json())
                    .then(() => toast.success("Kill-switch activated"))
                    .catch(() => toast.error("Kill-switch request failed"));
                }}
              >
                Activate Kill-switch
              </button>
            </div>
          </NeonCard>
        </div>
      </aside>
    </div>
  );
}
