import React from "react";

export default function FailsafePage({ failsafe }) {
  return (
    <div className="card-glass p-4 rounded-2xl">
      <h2 className="text-xl font-bold mb-4">Failsafe Control</h2>

      <p className="mb-4 text-slate-600">
        Current action: <strong>{failsafe.action}</strong>
      </p>

      <button className="px-4 py-2 bg-red-600 text-white rounded-lg">
        Trigger Kill Switch
      </button>
    </div>
  );
}
