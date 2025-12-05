import axios from "axios";
import { API_BASE } from "../config";

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 5000
});
export async function getVerificationStatus() {
  try {
    const backend = localStorage.getItem("BACKEND_URL") || "http://127.0.0.1:8000";
    const r = await fetch(`${backend}/pi/verify`);
    
    if (!r.ok) throw new Error("Backend returned error");

    return await r.json();
  } catch (err) {
    return { status: "error", error: err.message };
  }
}
