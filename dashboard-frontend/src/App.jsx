import React, { useEffect, useState } from "react";
import { Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";

import Dashboard from "./pages/Dashboard";
import MapPage from "./pages/MapPage";
import DetectorsPage from "./pages/DetectorsPage";
import FailsafePage from "./pages/FailsafePage";

const BACKEND_IP = "127.0.0.1";
const WS_URL = `ws://${BACKEND_IP}:8000/ws/frontend`;

export default function App() {
  const [telemetry, setTelemetry] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [failsafe, setFailsafe] = useState({ action: "NONE" });
  const [status, setStatus] = useState("SAFE");

  useEffect(() => {
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => console.log("Connected to backend WS");
    ws.onmessage = (ev) => {
      const msg = JSON.parse(ev.data);

      if (msg.type === "telemetry") {
        setTelemetry((prev) => [...prev, msg.payload].slice(-2000));

        if (msg.alerts && msg.alerts.length) {
          setAlerts((prev) => [...msg.alerts, ...prev].slice(0, 60));
          setStatus("ATTACK");
          setTimeout(() => setStatus("SAFE"), 3500);
        }

        if (msg.failsafe) setFailsafe(msg.failsafe);
      }
    };

    ws.onclose = () => console.log("WS closed");
    return () => ws.close();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />

      <div className="max-w-[1400px] mx-auto px-4 lg:px-6 py-6 grid grid-cols-12 gap-6">

        <aside className="col-span-12 lg:col-span-3 relative z-30">
          <Sidebar />
        </aside>

        <main className="col-span-12 lg:col-span-9 relative z-20">
          <Routes>
            <Route
              path="/"
              element={
                <Dashboard
                  telemetry={telemetry}
                  alerts={alerts}
                  status={status}
                  failsafe={failsafe}
                />
              }
            />
            <Route
              path="/map"
              element={<MapPage telemetry={telemetry} />}
            />
            <Route
              path="/detectors"
              element={<DetectorsPage alerts={alerts} telemetry={telemetry} />}
            />
            <Route
              path="/failsafe"
              element={<FailsafePage failsafe={failsafe} />}
            />
          </Routes>
        </main>

      </div>
    </div>
  );
}
