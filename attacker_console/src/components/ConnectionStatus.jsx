import React, { useState } from 'react'
import { testConnectivity } from '../utils/api'

export default function ConnectionStatus({ backendUrl, onSave, connected, lastSeen, pushLog }) {
  const [url, setUrl] = useState(backendUrl)
  const [checking, setChecking] = useState(false)

  const handleSave = async () => {
    setChecking(true)
    try {
      await testConnectivity(url)
      onSave(url)
      pushLog({ ts: new Date().toISOString(), type: 'info', msg: `Saved backend URL: ${url}` })
      alert('Connection OK - URL saved.')
    } catch (err) {
      pushLog({ ts: new Date().toISOString(), type: 'error', msg: `Save failed: ${err.message}` })
      alert('Unable to reach backend. Save aborted.')
    } finally {
      setChecking(false)
    }
  }

  return (
    <div className="card">
      <div style={{display:'flex',gap:8,alignItems:'center'}}>
        <div style={{flex:1}}>
          <div className="label">Backend URL</div>
          <input className="input" value={url} onChange={(e)=>setUrl(e.target.value)} />
        </div>
        <div style={{width:160}}>
          <button className="bigbtn" onClick={handleSave} disabled={checking}>
            {checking ? 'Checking...' : 'Save / Connect'}
          </button>
        </div>
      </div>

      <div style={{marginTop:12}}>
        <div>
          <span className="status-dot" style={{background: connected ? '#3ddc84' : '#ff6b6b'}}></span>
          <strong>{connected ? 'Connected' : 'Disconnected'}</strong>
          <span style={{marginLeft:10,color:'#666'}}>{lastSeen ? `Last: ${lastSeen}` : ''}</span>
        </div>
        <div style={{marginTop:8,fontSize:13,color:'#666'}}>Test endpoint: <code>/pi/attack-state</code></div>
      </div>
    </div>
  )
}
