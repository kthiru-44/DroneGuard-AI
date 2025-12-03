// api.js - local-only enforcement
export async function postAttack(baseUrl, params = {}) {
  const allowed = ["http://127.0.0.1:8000", "http://localhost:8000"];
  if (!allowed.includes(baseUrl.replace(/\/$/,''))) {
    throw new Error("Only local backend allowed in this demo");
  }
  const qs = new URLSearchParams(params).toString();
  const url = `${baseUrl.replace(/\/$/,'')}/attack?${qs}`;
  const res = await fetch(url, { method: "POST" });
  if (!res.ok) throw new Error("HTTP " + res.status);
  return res.json();
}

export async function clearAttack(baseUrl) {
  const allowed = ["http://127.0.0.1:8000", "http://localhost:8000"];
  if (!allowed.includes(baseUrl.replace(/\/$/,''))) {
    throw new Error("Only local backend allowed in this demo");
  }
  const url = `${baseUrl.replace(/\/$/,'')}/attack/clear`;
  const res = await fetch(url, { method: "POST" });
  if (!res.ok) throw new Error("HTTP " + res.status);
  return res.json();
}
