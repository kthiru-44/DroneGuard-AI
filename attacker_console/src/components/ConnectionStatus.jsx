import React, { useState } from 'react'
import { testConnectivity } from '../utils/api'

export default function ConnectionStatus({ backendUrl, onSave, connected, lastSeen, pushLog }) {
  const [url, setUrl] = useState(backendUrl)
  const [checking, setChecking] = useState(false)
  const [searching, setSearching] = useState(false)

  const handleSave = async () => {
    setChecking(true)
    try {
      await testConnectivity(url)
      onSave(url)
      pushLog({ ts: new Date().toISOString(), type: 'info', msg: `Saved backend URL: ${url}` })
      alert('Connection OK — URL saved.')
    } catch (err) {
      pushLog({ ts: new Date().toISOString(), type: 'error', msg: `Save failed: ${err.message}` })
      alert('Unable to reach backend.')
    } finally {
      setChecking(false)
    }
  }

  const autoDiscover = async () => {
    setSearching(true)
    const guess = "http://droneguard.local:8000"

    try {
      const res = await testConnectivity(guess)
      if (res) {
        setUrl(guess)
        onSave(guess)
        pushLog({ ts: new Date().toISOString(), type: 'info', msg: 'Auto-discovery success. Found DroneGuard at droneguard.local' })
        alert("DroneGuard Control Center Found!")
      }
    } catch (error) {
      pushLog({ ts: new Date().toISOString(), type: 'error', msg: 'Auto-discovery failed' })
      alert("Control Center not found on network.")
    }
    setSearching(false)
  }

  return (
    <div className="card">

      <div style={{display:'flex',gap:8,alignItems:'center'}}>
        <div style={{flex:1}}>
          <div className="label">Backend URL</div>
          <input 
            className="input" 
            value={url}
            onChange={(e)=>setUrl(e.target.value)}
          />
        </div>

        <div style={{width:160}}>
          <button 
            className="bigbtn" 
            onClick={handleSave} 
            disabled={checking}
          >
            {checking ? 'Checking…' : 'Save / Connect'}
          </button>
        </div>
      </div>

      <div style={{marginTop:10}}>
        <button 
          className="bigbtn" 
          style={{background:'#005eff',color:'#fff',width:'100%'}}
          onClick={autoDiscover}
          disabled={searching}
        >
          {searching ? 'Searching…' : 'Search Control Center'}
        </button>
      </div>

      <div style={{marginTop:12}}>
        <span 
          className="status-dot" 
          style={{background: connected ? '#3ddc84' : '#ff6b6b'}}
        />
        <strong>{connected ? 'Connected' : 'Disconnected'}</strong>
        <span style={{marginLeft:10,color:'#666'}}>
          {lastSeen ? `Last: ${lastSeen}` : ''}
        </span>

      </div>

    </div>
  )
}
