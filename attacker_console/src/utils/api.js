// api.js - local-only enforcement and fetch helpers
const DEFAULT_LOCALS = ['http://localhost:8000', 'http://127.0.0.1:8000']

// Set to true only if you intentionally want to allow remote backends.
// Leave false for safe default.
const ALLOW_REMOTE = true

function isLocal(url) {
  try {
    const u = new URL(url)
    return DEFAULT_LOCALS.includes(u.origin)
  } catch(e){ return false }
}

// Simple backoff retry
async function fetchWithRetry(url, options = {}, retries = 2, backoff = 300) {
  for (let i = 0; i <= retries; i++) {
    try {
      const res = await fetch(url, options)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      // try to parse JSON, fallback to text
      const ct = res.headers.get('content-type') || ''
      const body = ct.includes('application/json') ? await res.json() : await res.text()
      return { status: 'ok', body, statusCode: res.status }
    } catch (err) {
      if (i === retries) throw err
      await new Promise(r => setTimeout(r, backoff * (i+1)))
    }
  }
}

// Exported functions
export async function testConnectivity(baseUrl) {
  if (!ALLOW_REMOTE && !isLocal(baseUrl)) throw new Error('Remote backends not allowed in this build (safe default)')
  const url = `${baseUrl.replace(/\/$/, '')}/pi/attack-state`
  const res = await fetchWithRetry(url, { method: 'GET' }, 1, 200)
  return res.body
}

export async function postAttack(baseUrl, params = {}) {
  if (!ALLOW_REMOTE && !isLocal(baseUrl)) throw new Error('Remote backends not allowed in this build (safe default)')
  const qs = new URLSearchParams(params).toString()
  const url = `${baseUrl.replace(/\/$/, '')}/attack${qs ? '?' + qs : ''}`
  return await fetchWithRetry(url, { method: 'POST' }, 2, 300)
}

export async function clearAttack(baseUrl) {
  if (!ALLOW_REMOTE && !isLocal(baseUrl)) throw new Error('Remote backends not allowed in this build (safe default)')
  const url = `${baseUrl.replace(/\/$/, '')}/attack/clear`
  return await fetchWithRetry(url, { method: 'POST' }, 2, 300)
}
