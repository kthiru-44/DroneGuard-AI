import React from "react";
import { Routes, Route } from "react-router-dom";
import Dashboard from "../pages/Dashboard";
import MapPage from "../pages/MapPage";
import Detectors from "../pages/Detectors";
import Failsafe from "../pages/Failsafe";

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/map" element={<MapPage />} />
      <Route path="/detectors" element={<Detectors />} />
      <Route path="/failsafe" element={<Failsafe />} />
    </Routes>
  );
}
