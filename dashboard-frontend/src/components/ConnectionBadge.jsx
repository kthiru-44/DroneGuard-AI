import React from "react";
import { useTelemetry } from "../hooks/useTelemetry";
import React, { useEffect, useState } from "react";
import { getVerificationStatus } from "../services/api"; // you will create this

export default function ConnectionBadge({ connected }) {
  const [verified, setVerified] = useState(null);

  useEffect(() => {
    async function check() {
      try {
        const res = await getVerificationStatus();
        setVerified(res.signature_ok);
      } catch {
        setVerified(false);
      }
    }
    check();
    const interval = setInterval(check, 5000); // poll every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="conn-badge">
      <div className={`dot ${connected ? "ok" : "no"}`} />
      <span>{connected ? "CONNECTED" : "OFFLINE"}</span>

      {/* --- NEW VERIFICATION INDICATOR --- */}
      {verified === null && (
        <span className="verify pending">Verifying…</span>
      )}

      {verified === true && (
        <span className="verify good">✔ Secure Stream Verified</span>
      )}

      {verified === false && (
        <span className="verify bad">⚠ Unverified — Tampering Suspected!</span>
      )}
    </div>
  );
}


export default function ConnectionBadge() {
  const { connected } = useTelemetry();
  return (
    <div className={`px-3 py-1 rounded-md text-sm font-semibold ${connected ? "bg-green-600/20 text-green-300" : "bg-red-600/20 text-red-300"}`}>
      {connected ? "Connected" : "Disconnected"}
    </div>
  );
}
