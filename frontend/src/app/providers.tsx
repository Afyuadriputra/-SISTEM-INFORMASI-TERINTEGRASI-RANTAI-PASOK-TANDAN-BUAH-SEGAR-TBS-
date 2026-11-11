import { QueryClientProvider } from '@tanstack/react-query';
import { useEffect, type ReactNode } from 'react';
import { setUnauthorizedHandler } from '@/lib/api/client';
import { appQueryClient, clearSessionState } from '@/lib/query/queryClient';
import { useUiStore } from '@/lib/state/uiStore';
import { appRouter } from './router/router';

export function AppProviders({ children }: { readonly children: ReactNode }) {
  useEffect(() => {
    setUnauthorizedHandler(() => {
      clearSessionState(appQueryClient);
      useUiStore.getState().setSessionExpiredBanner(true);
      void appRouter.navigate({ to: '/login', replace: true });
    });
    return () => setUnauthorizedHandler(null);
  }, []);

  return <QueryClientProvider client={appQueryClient}>{children}</QueryClientProvider>;
}
