import React from "react";
import MapView from "../components/MapView";

export default function MapPage({ telemetry }) {
  return (
    <div className="card-glass p-4 rounded-2xl">
      <h2 className="text-xl font-bold mb-4">Live Map</h2>
      <MapView telemetry={telemetry} />
    </div>
  );
}
