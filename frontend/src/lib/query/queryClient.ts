import { QueryClient } from '@tanstack/react-query';
import { ApiError } from '@/lib/errors/errorCatalog';
import { useUiStore } from '@/lib/state/uiStore';

export function createAppQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        gcTime: 5 * 60_000,
        retry: (failureCount, error) => {
          if (error instanceof ApiError) {
            if (error.status >= 400 && error.status < 500) {
              return false;
            }
            return error.retryable && failureCount < 1;
          }
          return failureCount < 1;
        },
        refetchOnWindowFocus: false,
      },
      mutations: {
        retry: false,
      },
    },
  });
}

export const appQueryClient = createAppQueryClient();

/**
 * Purges all cached queries & pending ephemeral UI keys so no private data leaks across sessions.
 */
export function clearSessionState(client: QueryClient = appQueryClient): void {
  client.clear();
  useUiStore.getState().resetEphemeralState();
}
