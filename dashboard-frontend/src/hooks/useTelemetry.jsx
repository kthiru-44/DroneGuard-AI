// src/hooks/useTelemetry.jsx
import React, { createContext, useContext, useEffect, useState } from "react";
import { createWsClient } from "../services/wsClient";
import toast from "react-hot-toast";
import { WS_URL } from "../config";

export const TelemetryContext = createContext(null);

export function TelemetryProvider({ children }) {
  const [telemetry, setTelemetry] = useState([]); 
  const [alerts, setAlerts] = useState([]);
  const [failsafe, setFailsafe] = useState({ active: false, reason: null });
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = createWsClient(WS_URL);

    ws.addEventListener("open", () => {
      setConnected(true);
      toast.success("Connected to backend");
    });

    ws.addEventListener("close", () => {
      setConnected(false);
      toast.error("Disconnected from backend");
    });

    ws.addEventListener("message", (ev) => {
      try {
        const msg = JSON.parse(ev.data);

        // TELEMETRY -------------------------------------
        if (msg.type === "telemetry" && msg.payload) {
          const p = msg.payload;

          const t = {
            time: p.time || Date.now() / 1000,
            gps_lat: typeof p.gps_lat === "number" ? p.gps_lat : null,
            gps_lon: typeof p.gps_lon === "number" ? p.gps_lon : null,
            roll: p.roll ?? null,
            pitch: p.pitch ?? null,
            yaw: p.yaw ?? null,
            altitude: p.altitude ?? null,
            speed: p.speed ?? null,
            source: p.source || "normal",
            raw: p
          };

          setTelemetry((old) => [t, ...old].slice(0, 2000));
        }

        // ALERTS -------------------------------------
        else if (msg.type === "alert" && msg.payload) {
          const arr = Array.isArray(msg.payload) ? msg.payload : [msg.payload];
          setAlerts((old) => [...arr, ...old].slice(0, 500));
        }

        // FAILSAFE -------------------------------------
        else if (msg.type === "failsafe" && msg.payload) {
          setFailsafe(msg.payload);
        }
      } catch (e) {
        console.warn("Malformed WS message:", e);
      }
    });

    return () => ws.close();
  }, []);

  return (
    <TelemetryContext.Provider value={{ telemetry, alerts, failsafe, connected }}>
      {children}
    </TelemetryContext.Provider>
  );
}

export const useTelemetry = () => {
  return useContext(TelemetryContext);
};
