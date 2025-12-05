import React, { useEffect, useState } from "react";
import { useTelemetry } from "../hooks/useTelemetry";
import { getVerificationStatus } from "../services/api";


export default function ConnectionBadge() {
  const { connected } = useTelemetry();
  const [verified, setVerified] = useState(false);

  useEffect(() => {
    async function check() {
      try {
        const r = await getVerificationStatus();
        setVerified(r.valid === true);
      } catch {
        setVerified(false);
      }
    }
    check();
  }, []);

  return (
    <div
      className={`px-3 py-1 rounded-md text-sm font-semibold ${
        connected
          ? "bg-green-600/20 text-green-300"
          : "bg-red-600/20 text-red-300"
      }`}
    >
      {connected ? "Connected" : "Disconnected"} •{" "}
      {verified ? "Verified ✓" : "Unverified ✗"}
    </div>
  );
}

