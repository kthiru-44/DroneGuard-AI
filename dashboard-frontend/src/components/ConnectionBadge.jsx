import React from "react";
import { useTelemetry } from "../hooks/useTelemetry";

export default function ConnectionBadge() {
  const { connected } = useTelemetry();
  return (
    <div className={`px-3 py-1 rounded-md text-sm font-semibold ${connected ? "bg-green-600/20 text-green-300" : "bg-red-600/20 text-red-300"}`}>
      {connected ? "Connected" : "Disconnected"}
    </div>
  );
}
