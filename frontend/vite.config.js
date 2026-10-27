import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 前端全部走相对路径 /api/...，靠 Vite proxy 转发到后端，不硬编码域名
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})