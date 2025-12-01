import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // exposes to Windows + LAN
    port: 5174,
    strictPort: true
  }
})
