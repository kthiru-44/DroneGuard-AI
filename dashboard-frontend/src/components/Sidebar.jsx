import React from "react";
import { Link } from "react-router-dom";
import { MapPinIcon, CpuChipIcon, BoltIcon } from "@heroicons/react/24/outline";

export default function Sidebar() {
  return (
    <nav className="card-glass p-4 rounded-2xl space-y-2">

      <Link
        to="/"
        className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-100 transition"
      >
        <MapPinIcon className="w-5 h-5 text-teal-600" />
        <span className="text-sm font-medium">Dashboard</span>
      </Link>

      <Link
        to="/map"
        className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-100 transition"
      >
        <MapPinIcon className="w-5 h-5 text-green-600" />
        <span className="text-sm font-medium">Live Map</span>
      </Link>

      <Link
        to="/detectors"
        className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-100 transition"
      >
        <CpuChipIcon className="w-5 h-5 text-amber-600" />
        <span className="text-sm font-medium">Detectors</span>
      </Link>

      <Link
        to="/failsafe"
        className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-100 transition"
      >
        <BoltIcon className="w-5 h-5 text-red-600" />
        <span className="text-sm font-medium">Failsafe</span>
      </Link>

    </nav>
  );
}
