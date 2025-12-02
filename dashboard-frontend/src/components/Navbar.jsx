import React from "react";
import { BellIcon } from "@heroicons/react/24/outline";

export default function Navbar() {
  return (
    <header className="w-full h-16 px-6 flex items-center justify-between bg-white/70 backdrop-blur-md border-b border-slate-200 shadow-sm relative z-40">
      
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-teal-600 text-white flex items-center justify-center font-bold">
          DG
        </div>
        <div>
          <h1 className="text-lg font-bold text-slate-800 leading-none">DroneGuard AI</h1>
          <p className="text-xs text-slate-500">Telemetry Intrusion Protection</p>
        </div>
      </div>

      <div className="flex items-center gap-4 text-slate-600">
        <BellIcon className="w-6 h-6" />
        <span className="text-sm font-medium">Vijay M</span>
      </div>

    </header>
  );
}
