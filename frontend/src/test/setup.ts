import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterAll, afterEach, beforeAll } from 'vitest';
import { clearCsrfToken } from '@/lib/api/client';
import { clearSessionState } from '@/lib/query/queryClient';
import { resetMockDb } from '@/mocks/mockDb';
import { server } from '@/mocks/server';

beforeAll(() => {
  if (typeof window !== 'undefined') {
    window.scrollTo = () => undefined;
  }
  server.listen({ onUnhandledFrame: 'error' });
});

afterEach(() => {
  cleanup();
  server.resetHandlers();
  resetMockDb();
  clearCsrfToken();
  clearSessionState();
});

afterAll(() => {
  server.close();
});
