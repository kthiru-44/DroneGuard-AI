import React from "react";
import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard" },
  { to: "/map", label: "Live Map" },
  { to: "/detectors", label: "Detectors" },
  { to: "/failsafe", label: "Failsafe" }
];

export default function Sidebar() {
  return (
    <aside className="w-64 p-4 border-r border-white/6 bg-gradient-to-b from-[#041022] to-[#060616]">
      <div className="mb-6 text-neonPink font-semibold uppercase">Cyberpunk UI</div>
      <nav className="flex flex-col gap-2">
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            className={({ isActive }) => `px-3 py-2 rounded-md ${isActive ? "bg-neonCyan/10 text-neonCyan" : "text-white/60 hover:bg-white/5"}`}
          >
            {l.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
