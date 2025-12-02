import React from "react";
import { MapContainer, TileLayer, Polyline, Marker } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export default function MapView({ telemetry }) {
  const gps = telemetry.filter(p => p.gps_lat && p.gps_lon);
  const last = gps[gps.length - 1];

  return (
    <div
      className="rounded-xl overflow-hidden pointer-events-none"
      style={{ height: 420 }}
    >
      {gps.length === 0 ? (
        <div className="h-full flex items-center justify-center text-slate-400">
          Waiting for GPS telemetry...
        </div>
      ) : (
        <MapContainer
          center={[last.gps_lat, last.gps_lon]}
          zoom={18}
          style={{ height: "100%" }}
          className="pointer-events-none"
        >
          <TileLayer url="https://tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <Polyline positions={gps.map(p => [p.gps_lat, p.gps_lon])} />
          <Marker position={[last.gps_lat, last.gps_lon]} />
        </MapContainer>
      )}
    </div>
  );
}
