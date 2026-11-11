import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import { isMockApiMode } from './lib/config/env';
import './index.css';

async function bootstrapApplication() {
  if (import.meta.env.VITE_API_MODE !== 'real' && isMockApiMode()) {
    const { startMockServiceWorker } = await import('./mocks/browser');
    await startMockServiceWorker();
  }

  const rootElement = document.getElementById('root');
  if (!rootElement) {
    throw new Error('Elemen #root tidak ditemukan di index.html.');
  }

  createRoot(rootElement).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
}

void bootstrapApplication();
