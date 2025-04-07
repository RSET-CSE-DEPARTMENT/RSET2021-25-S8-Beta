import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server:{
    port:3000,
    proxy: {
      '/signin': 'http://localhost:5000',
      '/getUser': 'http://localhost:5000',
      '/clearUser': 'http://localhost:5000',
      '/videotranscription': 'http://localhost:5000',
      '/summarization': 'http://localhost:5000',
      '/SearchAndFilter': 'http://localhost:5000',
      '/get_signs' : 'http://localhost:5000',
      '/showQuestions' : 'http://localhost:5000'
    }
  }
})
