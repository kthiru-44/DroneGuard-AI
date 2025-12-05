import React from 'react'
import AttackButton from './AttackButton'
import { postAttack, clearAttack } from '../utils/api'

export default function AttackPanel({ backendUrl, pushLog }) {

  const trigger = async (mode) => {
    pushLog({ ts:new Date().toISOString(), type:'action', msg:`Send ${mode}` })
    await postAttack(backendUrl, { mode, mag:1, style:'sudden', dur:8 })
  }

  const clearAll = async () => {
    pushLog({ ts:new Date().toISOString(), type:'action', msg:'Clear Attack' })
    await clearAttack(backendUrl)
  }

  return (
    <div className="card">
      <h2 style={{textAlign:'center', color:'#00eaff'}}>Attack Commands</h2>

      <div className="attack-grid">

        <div>
          <AttackButton
            label="GPS Spoof"
            onClick={()=>trigger('GPS_SPOOF')}
          />
        </div>

        <div>
          <AttackButton
            label="IMU Injection"
            onClick={()=>trigger('IMU_INJECTION')}
          />
        </div>

        <div>
          <AttackButton
            label="Mode Hijack"
            onClick={()=>trigger('MODE_HIJACK')}
          />
        </div>

        <div>
          <AttackButton
            label="Jamming"
            onClick={()=>trigger('JAMMING')}
          />
        </div>

        <div className="full-row">
          <button className="bigbtn clear-btn" onClick={clearAll}>
            CLEAR ATTACK
          </button>
        </div>

      </div>
    </div>
  )
}
