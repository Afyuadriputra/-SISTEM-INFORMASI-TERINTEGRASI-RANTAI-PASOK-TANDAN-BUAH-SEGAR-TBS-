import path from 'node:path';
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  optimizeDeps: {
    exclude: ['maplibre-gl'],
  },
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
      '@contracts-fixtures': path.resolve(import.meta.dirname, '../contracts/fixtures'),
    },
  },
  server: {
    port: 5173,
    strictPort: true,
    fs: {
      allow: ['..'],
    },
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: false,
      },
      '/health': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: false,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('maplibre-gl')) {
            return 'vendor-maplibre';
          }
          if (id.includes('msw')) {
            return 'vendor-msw';
          }
          if (id.includes('react-dom') || id.includes(`${path.sep}react${path.sep}`)) {
            return 'vendor-react';
          }
          if (id.includes('@tanstack')) {
            return 'vendor-tanstack';
          }
          if (id.includes('react-hook-form') || id.includes('zod')) {
            return 'vendor-forms';
          }
          if (id.includes('node_modules')) {
            return 'vendor-core';
          }
          return undefined;
        },
      },
    },
  },
});
