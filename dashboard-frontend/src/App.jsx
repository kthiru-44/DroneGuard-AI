import React from "react";
import AppRouter from "./router/AppRouter";
import Sidebar from "./components/Sidebar";
import TopBar from "./components/TopBar";

export default function App() {
  return (
    <div className="min-h-screen bg-cyberBg text-white">
      <TopBar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <AppRouter />
        </main>
      </div>
    </div>
  );
}
