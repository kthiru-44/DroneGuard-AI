import React from 'react'

export default function Logs({ logs, onClear, onExport }) {
  return (
    <div className="card">
      <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
        <div className="label">Logs</div>
        <div>
          <button className="preset-btn" onClick={onExport}>Export</button>
          <button className="preset-btn" onClick={onClear}>Clear</button>
        </div>
      </div>

      <div style={{marginTop:8,maxHeight:520,overflow:'auto'}}>
        {logs.length===0 && <div style={{color:'#666'}}>No logs yet</div>}
        {logs.map((l, idx)=>(
          <div className="log-item" key={idx}>
            <div style={{fontSize:12,color:'#666'}}>{new Date(l.ts).toLocaleString()} · {l.type}</div>
            <div style={{marginTop:6}}>{l.msg}</div>
            {l.detail && <pre style={{whiteSpace:'pre-wrap',marginTop:6,fontSize:12}}>{JSON.stringify(l.detail,null,2)}</pre>}
          </div>
        ))}
      </div>
    </div>
  )
}
