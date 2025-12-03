import { useEffect, useRef } from "react";
import L from "leaflet";
import { useMap } from "react-leaflet";

export default function AnimatedMarker({ position, icon }) {
  const map = useMap();
  const markerRef = useRef(null);

  useEffect(() => {
    if (!position) return;
    if (!markerRef.current) {
      markerRef.current = L.marker(position, { icon }).addTo(map);
    } else {
      // animate: use small interval to step towards position
      const cur = markerRef.current.getLatLng();
      const target = L.latLng(position);
      const steps = 8;
      let i = 0;
      const latStep = (target.lat - cur.lat) / steps;
      const lngStep = (target.lng - cur.lng) / steps;
      const handle = setInterval(() => {
        i++;
        const next = L.latLng(cur.lat + latStep * i, cur.lng + lngStep * i);
        markerRef.current.setLatLng(next);
        if (i >= steps) clearInterval(handle);
      }, 40);
      return () => clearInterval(handle);
    }
  }, [position, map, icon]);

  return null;
}
