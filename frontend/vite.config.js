import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueJsx(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    // Specify the output directory
    outDir: './src/service/frontend',
    // Optional: Specify assets directory inside outDir (e.g., service/frontend/static)
    assetsDir: 'static',
    // Optional: Clean the output directory before building
    emptyOutDir: true
  }
})
