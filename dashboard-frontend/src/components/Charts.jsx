import React from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  LineElement,
  LinearScale,
  PointElement,
  CategoryScale,
  Tooltip,
  Legend
} from "chart.js";

ChartJS.register(LineElement, LinearScale, PointElement, CategoryScale, Tooltip, Legend);

export default function Charts({ telemetry, metric="altitude" }) {
  const last = telemetry.slice(-200);
  const values = last.map(p => p[metric] ?? 0);
  const labels = values.map(() => "");

  const data = {
    labels,
    datasets: [
      {
        label: metric,
        data: values,
        fill: true,
        tension: 0.2,
        borderWidth: 2,
        pointRadius: 0
      }
    ]
  };

  return <Line data={data} options={{ plugins:{legend:{display:false}}, scales:{y:{beginAtZero:true}} }} />;
}
