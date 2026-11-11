import { setupWorker } from 'msw/browser';
import { handlers } from './handlers';

export const worker = setupWorker(...handlers);

export async function startMockServiceWorker(): Promise<void> {
  await worker.start({
    onUnhandledFrame: 'bypass',
  });
}
