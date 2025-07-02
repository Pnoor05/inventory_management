import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@utils': path.resolve(__dirname, './src/utils')
    }
  },
  build: {
    outDir: '../static/dist',
    emptyOutDir: true,
    rollupOptions: {
      input: path.resolve(__dirname, 'index.html'),  // ✅ FIXED HERE
      output: {
        entryFileNames: 'temp_bill/[name].js',
        chunkFileNames: 'temp_bill/[name].js',
        assetFileNames: 'temp_bill/[name].[ext]'
      }
    }
  },
  server: {
    proxy: {
      '/api': 'http://localhost:5000'
    }
  }
})
