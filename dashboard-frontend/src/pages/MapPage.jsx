import React, { useMemo } from "react";
import { MapContainer, TileLayer, Polyline, useMap } from "react-leaflet";
import L from "leaflet";
import { useTelemetry } from "../hooks/useTelemetry";
import AnimatedMarker from "../components/AnimatedMarker";
import { interpolatePath } from "../utils/smoothing";

// Leaflet markers (Vite-compatible)
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerIcon2x from "leaflet/dist/images/marker-icon-2x.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";

// Fallback neon icon = normal marker
const neonMarker = markerIcon;

// Fix Leaflet default marker paths for Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow
});

// Neon marker icon
const NeonMarkerIcon = new L.Icon({
  iconUrl: neonMarker,
  iconSize: [30, 45],
  iconAnchor: [15, 45]
});

// Auto-center camera on drone
function CenterToPosition({ pos }) {
  const map = useMap();
  if (pos) {
    map.setView(pos, map.getZoom(), {
      animate: true,
      duration: 0.6
    });
  }
  return null;
}

export default function MapPage() {
  const { telemetry } = useTelemetry();

  const { normalTrack, injectedTrack, lastPos } = useMemo(() => {
    const normal = [];
    const injected = [];

    telemetry.slice().reverse().forEach((t) => {
      if (!t || t.gps_lat == null) return;
      const p = [t.gps_lat, t.gps_lon];

      if (t.source === "injected") injected.push(p);
      else normal.push(p);
    });

    return {
      normalTrack: interpolatePath(normal, 6),
      injectedTrack: interpolatePath(injected, 6),
      lastPos: telemetry[0] || null
    };
  }, [telemetry]);

  const center = lastPos
    ? [lastPos.gps_lat, lastPos.gps_lon]
    : [12.9716, 77.5946];

  const animatedPosition = lastPos
    ? [lastPos.gps_lat, lastPos.gps_lon]
    : null;

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-neonCyan">Live Map</h2>
      </div>

      <div className="rounded-xl overflow-hidden border border-white/10 shadow-neon">
        <MapContainer
          center={center}
          zoom={17}
          style={{ height: "70vh", width: "100%" }}
        >
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

          {/* Blue normal track */}
          {normalTrack.length > 1 && (
            <Polyline
              positions={normalTrack}
              pathOptions={{ color: "#3de3f2", weight: 3 }}
            />
          )}

          {/* Red injected track */}
          {injectedTrack.length > 1 && (
            <Polyline
              positions={injectedTrack}
              pathOptions={{ color: "#ff2d95", weight: 4 }}
            />
          )}

          {/* Animated Marker */}
          {animatedPosition && (
            <AnimatedMarker
              position={animatedPosition}
              icon={NeonMarkerIcon}
            />
          )}

          <CenterToPosition pos={animatedPosition} />
        </MapContainer>
      </div>
    </div>
  );
}
