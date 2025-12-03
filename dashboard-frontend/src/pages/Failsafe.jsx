import React, { useState } from "react";
import NeonCard from "../components/NeonCard";
import axios from "axios";
import { API_BASE } from "../config";
import toast from "react-hot-toast";

export default function Failsafe() {
  const [loading, setLoading] = useState(false);

  const activateFailsafe = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/failsafe/reset`); // demo: call your failsafe endpoint or /attack?mode=...
      toast.success("Failsafe activated (demo)");
    } catch (e) {
      toast.error("Error activating failsafe: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <NeonCard>
        <h3 className="text-neonCyan">Failsafe Controls</h3>
        <div className="mt-4">
          <button onClick={activateFailsafe} disabled={loading} className="px-4 py-2 rounded bg-neonPink text-black">
            Activate Kill-switch
          </button>
        </div>
      </NeonCard>
    </div>
  );
}
