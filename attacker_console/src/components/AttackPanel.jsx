import React, { useState, useEffect } from 'react'
import AttackButton from './AttackButton'
import { postAttack, clearAttack } from '../utils/api'

const PRESETS = {
  'Quick Spoof': [{ mode:'GPS_SPOOF', mag:2.0, style:'sudden', dur:10 }],
  'Stealth Drift': [{ mode:'GPS_SPOOF', mag:0.2, style:'gradual', dur:30 }],
  'Full Hijack': [{ mode:'MODE_HIJACK', mag:1, style:'sudden', dur:8 }, { mode:'JAMMING', mag:1, style:'sudden', dur:10 }]
}

export default function AttackPanel({ backendUrl, pushLog }) {
  const [activeConfig, setActiveConfig] = useState(null)
  const [running, setRunning] = useState(false)

  useEffect(() => {
  // helper: return true if focus is inside an editable control
  const isTypingInInput = (e) => {
    const el = document.activeElement
    if (!el) return false
    const tag = el.tagName
    if (tag === 'INPUT' || tag === 'TEXTAREA' || el.isContentEditable) return true
    // also ignore when a select is focused
    if (tag === 'SELECT') return true
    return false
  }

  const handler = (e) => {
    // if user is typing in an input/select/textarea, do NOT trigger shortcuts
    if (isTypingInInput(e)) return

    // allow shortcuts only when focus is not on a form control
    switch (e.key) {
      case '1':
        trigger('GPS_SPOOF')
        break
      case '2':
        trigger('IMU_INJECTION')
        break
      case '3':
        trigger('MODE_HIJACK')
        break
      case '4':
        trigger('JAMMING')
        break
      case '5':
        clearAll()
        break
      default:
        break
    }
  }

  window.addEventListener('keydown', handler)
  return () => window.removeEventListener('keydown', handler)
}, [backendUrl])


  const sendAttack = async (params) => {
    if (!confirm('Confirm Action ?')) return
    pushLog({ ts:new Date().toISOString(), type:'action', msg:`Send ${params.mode} ${JSON.stringify(params)}` })
    try {
      const res = await postAttack(backendUrl, { mode: params.mode, mag: params.mag, style: params.style, dur: params.dur || 10 })
      pushLog({ ts:new Date().toISOString(), type:'resp', msg: JSON.stringify(res) })
      alert('Attack sent (mock) — see logs')
    } catch (err) {
      pushLog({ ts:new Date().toISOString(), type:'error', msg: err.message })
      alert('Error sending attack: ' + err.message)
    }
  }

  const trigger = (mode) => {
    setActiveConfig({ mode, mag: 1.0, style: 'sudden', dur: 8 })
    sendAttack({ mode, mag:1.0, style:'sudden', dur:8 })
  }

  const clearAll = async () => {
    if (!confirm('Clear attacks?')) return
    try {
      const res = await clearAttack(backendUrl)
      pushLog({ ts:new Date().toISOString(), type:'action', msg: 'Clear attack', detail: res })
      alert('Cleared (mock).')
    } catch (err) {
      pushLog({ ts:new Date().toISOString(), type:'error', msg: err.message })
      alert('Error clearing: ' + err.message)
    }
  }

  const runPreset = async (name) => {
    if (!confirm(`Run preset "${name}"?`)) return
    const seq = PRESETS[name]
    setRunning(true)
    for (let i=0;i<seq.length;i++){
      const p = seq[i]
      pushLog({ts:new Date().toISOString(), type:'seq', msg:`Preset ${name} step ${i+1}`, detail: p})
      try{
        await postAttack(backendUrl, { mode:p.mode, mag:p.mag, style:p.style, dur:p.dur })
      }catch(err){
        pushLog({ ts:new Date().toISOString(), type:'error', msg:err.message })
      }
      await new Promise(r=>setTimeout(r, 800 + (p.dur||5)*100))
    }
    setRunning(false)
    alert('Preset sequence finished (mock).')
  }

  return (
    <div className="card">
      <div className="label">Attack Panel</div>

      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10}}>
        <div>
          <AttackButton label="Inject GPS SPOOF" onClick={()=>trigger('GPS_SPOOF')} />
        </div>
        <div>
          <AttackButton label="Inject IMU INJECTION" onClick={()=>trigger('IMU_INJECTION')} />
        </div>
        <div>
          <AttackButton label="Inject MODE HIJACK" onClick={()=>trigger('MODE_HIJACK')} />
        </div>
        <div>
          <AttackButton label="Start JAMMING" onClick={()=>trigger('JAMMING')} />
        </div>
        <div>
          <AttackButton label="Delay / Reorder Packets" onClick={()=>trigger('DELAY_REORDER')} />
        </div>
        <div>
          <button className="bigbtn" onClick={clearAll} style={{background:'#6c757d',color:'#fff'}}>Clear Attack</button>
        </div>
      </div>

      <div style={{marginTop:12}}>
        <div className="label">Presets</div>
        <div className="preset-row">
          {Object.keys(PRESETS).map((k)=>(
            <button key={k} className="preset-btn" onClick={()=>runPreset(k)} disabled={running}>{k}</button>
          ))}
        </div>
      </div>

      <div style={{marginTop:12}}>
        <div className="label">Custom Attack</div>
        <div style={{display:'flex',gap:8,alignItems:'center'}}>
          <select id="mode" defaultValue="GPS_SPOOF" onChange={(e)=>setActiveConfig({...activeConfig, mode:e.target.value})}>
            <option value="GPS_SPOOF">GPS_SPOOF</option>
            <option value="IMU_INJECTION">IMU_INJECTION</option>
            <option value="MODE_HIJACK">MODE_HIJACK</option>
            <option value="JAMMING">JAMMING</option>
            <option value="DELAY_REORDER">DELAY_REORDER</option>
          </select>
          <input type="number" className="input small" defaultValue={1.0} id="mag" step="0.1" />
          <select id="style">
            <option value="sudden">sudden</option>
            <option value="gradual">gradual</option>
          </select>
          <input type="number" className="input small" id="dur" defaultValue={10} />
          <button className="bigbtn" style={{width:140}} onClick={()=>{
            const mode = document.getElementById('mode').value
            const mag = parseFloat(document.getElementById('mag').value)
            const style = document.getElementById('style').value
            const dur = parseInt(document.getElementById('dur').value,10)
            sendAttack({ mode, mag, style, dur })
          }}>Send</button>
        </div>
      </div>
    </div>
  )
}
