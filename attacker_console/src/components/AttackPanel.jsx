import React, { useState, useEffect } from 'react'
import AttackButton from './AttackButton'
import { postAttack, clearAttack } from '../utils/api'

export default function AttackPanel({ backendUrl, pushLog }) {
  const [activeAttack, setActiveAttack] = useState(null)   // NEW

  useEffect(() => {
    const isTyping = () => {
      const el = document.activeElement
      if (!el) return false
      const tag = el.tagName
      return (
        tag === 'INPUT' ||
        tag === 'TEXTAREA' ||
        tag === 'SELECT' ||
        el.isContentEditable
      )
    }

    const handler = (e) => {
      if (isTyping()) return
      switch (e.key) {
        case '1': sendQuick('GPS_SPOOF'); break
        case '2': sendQuick('IMU_INJECTION'); break
        case '3': sendQuick('MODE_HIJACK'); break
        case '4': sendQuick('JAMMING'); break
        case '5': sendQuick('DELAY_REORDER'); break
        case '0': clearAll(); break
        default: break
      }
    }

    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [backendUrl])

  const sendQuick = async (mode) => {
    if (!confirm(`Confirm ${mode}?`)) return

    setActiveAttack(mode)   // NEW → Trigger banner

    const params = { mode, mag: 1.0, style: 'sudden', dur: 8 }
    pushLog({ ts:new Date().toISOString(), type:'action', msg:`Send ${mode}` })

    try {
      const res = await postAttack(backendUrl, params)
      pushLog({ ts:new Date().toISOString(), type:'resp', msg: JSON.stringify(res) })
      alert(`${mode} triggered.`)
    } catch (err) {
      alert('Error: ' + err.message)
    }
  }

  const clearAll = async () => {
    if (!confirm('Clear all attacks?')) return
    try {
      await clearAttack(backendUrl)
      setActiveAttack(null)   // NEW → Remove banner
      alert('Attacks cleared.')
    } catch (err) {
      alert('Error: ' + err.message)
    }
  }

  return (
    <div className="card">
      
      {/* 🔥 ACTIVE ATTACK BANNER */}
      {activeAttack && (
        <div className="active-banner">
          ACTIVE ATTACK: {activeAttack}
        </div>
      )}

      <div className="label">Attack Panel</div>

      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:10}}>
        <AttackButton label="GPS Spoof" onClick={()=>sendQuick('GPS_SPOOF')} />
        <AttackButton label="IMU Injection" onClick={()=>sendQuick('IMU_INJECTION')} />
        <AttackButton label="Mode Hijack" onClick={()=>sendQuick('MODE_HIJACK')} />
        <AttackButton label="Start Jamming" onClick={()=>sendQuick('JAMMING')} />
        <AttackButton label="Delay / Reorder" onClick={()=>sendQuick('DELAY_REORDER')} />
        <button 
          className="bigbtn" 
          onClick={clearAll} 
          style={{background:'#6c757d'}}
        >
          Clear Attack
        </button>
      </div>

    </div>
  )
}
