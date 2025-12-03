// src/components/MiniMap.jsx
import React from "react";
import { MapContainer, TileLayer, Polyline, Marker } from "react-leaflet";
import L from "leaflet";
import { useTelemetry } from "../hooks/useTelemetry";

// Fix Leaflet icons for Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL("leaflet/dist/images/marker-icon-2x.png", import.meta.url).href,
  iconUrl: new URL("leaflet/dist/images/marker-icon.png", import.meta.url).href,
  shadowUrl: new URL("leaflet/dist/images/marker-shadow.png", import.meta.url).href,
});

export default function MiniMap() {
  const { telemetry } = useTelemetry();

  // build safe GPS track
  const gpsTrack = Array.isArray(telemetry)
    ? telemetry
        .filter((t) => typeof t.gps_lat === "number" && typeof t.gps_lon === "number")
        .map((t) => [t.gps_lat, t.gps_lon])
    : [];

  // default center (if no telemetry)
  const last =
    gpsTrack.length > 0 ? gpsTrack[gpsTrack.length - 1] : [12.9716, 77.5946];

  return (
    <div className="w-full h-full rounded-lg overflow-hidden">
      <MapContainer
        center={last}
        zoom={17}
        zoomControl={false}
        scrollWheelZoom={false}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        {/* flight path */}
        {gpsTrack.length > 1 && (
          <Polyline positions={gpsTrack} pathOptions={{ color: "#00f0ff" }} />
        )}

        {/* drone marker */}
        <Marker position={last} />
      </MapContainer>
    </div>
  );
}
