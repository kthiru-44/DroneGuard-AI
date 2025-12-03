import React from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { TelemetryProvider } from "./hooks/useTelemetry";
import "./styles.css";
import "leaflet/dist/leaflet.css";
import { Toaster } from "react-hot-toast";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <BrowserRouter>
      <TelemetryProvider>
        <App />
        <Toaster position="top-right" />
      </TelemetryProvider>
    </BrowserRouter>
  </React.StrictMode>
);
