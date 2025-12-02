import React from "react";
import AlertsPanel from "../components/AlertsPanel";

export default function DetectorsPage({ alerts }) {
  return (
    <div className="card-glass p-4 rounded-2xl">
      <h2 className="text-xl font-bold mb-4">Detectors</h2>
      <AlertsPanel alerts={alerts} />
    </div>
  );
}
