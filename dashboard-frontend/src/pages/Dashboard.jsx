import React from "react";
import MapView from "../components/MapView";
import IMUGauge from "../components/IMUGauge";
import AlertsPanel from "../components/AlertsPanel";
import Charts from "../components/Charts";
import StatusBar from "../components/StatusBar";

export default function Dashboard({ telemetry, status, failsafe, alerts }) {
  return (
    <div className="space-y-6">

      <div className="card-glass p-4 rounded-2xl">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-slate-800">DroneGuard AI</h1>
            <p className="text-sm text-slate-500">
              Real-time telemetry & intrusion protection
            </p>
          </div>
          <div className="text-sm text-slate-500">
            Points: <span>{telemetry.length}</span>
          </div>
        </div>

        <div className="mt-4 grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="col-span-2">
            <MapView telemetry={telemetry} />
          </div>

          <div className="space-y-4">
            <div className="card-glass p-3 rounded-xl">
              <h4 className="text-sm font-semibold">Live IMU</h4>
              <IMUGauge telemetry={telemetry} />
            </div>

            <div className="card-glass p-3 rounded-xl">
              <h4 className="text-sm font-semibold">Latest Alerts</h4>
              <AlertsPanel alerts={alerts} compact />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card-glass p-4 rounded-2xl">
          <h3 className="text-sm font-semibold mb-3">Altitude</h3>
          <Charts telemetry={telemetry} metric="altitude" />
        </div>

        <div className="card-glass p-4 rounded-2xl">
          <h3 className="text-sm font-semibold mb-3">Yaw</h3>
          <Charts telemetry={telemetry} metric="yaw" />
        </div>
      </div>

    </div>
  );
}
