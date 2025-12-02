import React, { useState, useEffect, useCallback } from 'react'
import ConnectionStatus from './components/ConnectionStatus'
import AttackPanel from './components/AttackPanel'
import Logs from './components/Logs'
import { testConnectivity } from './utils/api'

export default function App() {
  const [backendUrl, setBackendUrl] = useState(() => {
    return localStorage.getItem('BACKEND_URL') || 'http://localhost:8000'
  })
  const [connected, setConnected] = useState(false)
  const [lastSeen, setLastSeen] = useState(null)
  const [logs, setLogs] = useState([])

  const pushLog = useCallback((entry) => {
    setLogs((s) => [entry, ...s].slice(0, 200))
  }, [])

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await testConnectivity(backendUrl)
        setConnected(true)
        setLastSeen(new Date().toLocaleTimeString())
        pushLog({ ts: new Date().toISOString(), type: 'connect', msg: `Ping OK: ${res}` })
      } catch (err) {
        setConnected(false)
        pushLog({ ts: new Date().toISOString(), type: 'error', msg: `Ping fail: ${err.message}` })
      }
    }, 6000)
    return () => clearInterval(interval)
  }, [backendUrl, pushLog])

  return (
    <div className="app">
      <header className="header">
        <h1>DroneGuard — Attacker Console (SIMULATION)</h1>
      </header>

      <main className="container">
        <section className="left">
          <ConnectionStatus
            backendUrl={backendUrl}
            onSave={(url) => {
              setBackendUrl(url)
              localStorage.setItem('BACKEND_URL', url)
            }}
            connected={connected}
            lastSeen={lastSeen}
            pushLog={pushLog}
          />

          <AttackPanel backendUrl={backendUrl} pushLog={pushLog} />
        </section>

        <aside className="right">
          <Logs logs={logs} onClear={() => setLogs([])} onExport={() => {
            const blob = new Blob([JSON.stringify(logs, null, 2)], { type: 'application/json' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = 'attacker-logs.json'
            a.click()
            URL.revokeObjectURL(url)
          }} />
        </aside>
      </main>

      <footer className="footer">Press keys 1..5 to trigger quick attacks</footer>
    </div>
  )
}
