import { useState } from "react";

export default function useTelemetry() {
  const [telemetry, setTelemetry] = useState([]);

  const add = (pkt) => {
    setTelemetry((prev) => [...prev, pkt].slice(-1500));
  };

  return { telemetry, add };
}
