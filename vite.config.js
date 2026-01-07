import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  build: {
    outDir: path.resolve(__dirname, 'static'), 
    assetsDir: 'assets',
    emptyOutDir: true, 
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000' 
    }
  }
})