import type { components } from '@/lib/api/generated';
import { apiRequest, clearCsrfToken, ensureCsrfToken } from '@/lib/api/client';
import type { AuthenticatedUser } from '@/lib/auth/permissions';
import { ApiError } from '@/lib/errors/errorCatalog';
import { clearSessionState } from '@/lib/query/queryClient';
import { useUiStore } from '@/lib/state/uiStore';

export type LoginRequest = components['schemas']['LoginRequest'];
export type AuthUserEnvelope = components['schemas']['AuthUserEnvelope'];

export async function fetchCurrentUser(): Promise<AuthenticatedUser | null> {
  try {
    const envelope = await apiRequest<AuthUserEnvelope>({
      path: '/api/v1/auth/me',
      method: 'GET',
      suppressUnauthorizedHook: true,
    });
    return envelope.data;
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      return null;
    }
    throw error;
  }
}

export async function loginWithCredentials(payload: LoginRequest): Promise<AuthenticatedUser> {
  clearSessionState();
  await ensureCsrfToken(true);
  const envelope = await apiRequest<AuthUserEnvelope>({
    path: '/api/v1/auth/login',
    method: 'POST',
    body: payload,
    suppressUnauthorizedHook: true,
  });
  // Refresh CSRF after session creation/rotation on login.
  await ensureCsrfToken(true);
  useUiStore.getState().setSessionExpiredBanner(false);
  return envelope.data;
}

export async function logoutSession(): Promise<void> {
  try {
    await apiRequest<{ success: true; data: Record<string, never> | null }>({
      path: '/api/v1/auth/logout',
      method: 'POST',
      suppressUnauthorizedHook: true,
    });
  } finally {
    clearCsrfToken();
    clearSessionState();
  }
}
