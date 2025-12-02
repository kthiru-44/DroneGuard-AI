import React from 'react'

export default function AttackButton({ label, color='#d9534f', onClick, shortcut }) {
  return (
    <button
      className="bigbtn attack-btn"
      style={{background: color}}
      onClick={onClick}
      title={shortcut ? `Shortcut: ${shortcut}` : undefined}
    >
      {label}
    </button>
  )
}
