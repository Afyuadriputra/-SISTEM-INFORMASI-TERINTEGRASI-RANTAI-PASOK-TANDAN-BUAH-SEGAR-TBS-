import { http } from 'msw';
import { MOCK_SIMULATION_PASSWORD, mockDb } from '../mockDb';
import {
  appendMockAuditEvent,
  assertMockCsrf,
  getAuthenticatedMockUser,
  makeErrorResponse,
  makeSimpleEnvelope,
} from '../utils';

export const authHandlers = [
  http.get('/api/v1/auth/csrf', () => {
    return makeSimpleEnvelope({
      csrf_token: mockDb.csrfToken,
      header_name: 'X-CSRF-Token' as const,
    });
  }),

  http.post('/api/v1/auth/login', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) {
      return csrfError;
    }

    const body = (await request.json().catch(() => null)) as {
      username?: string;
      password?: string;
    } | null;

    const username = body?.username?.trim();
    const password = body?.password;
    if (!username || !password) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }

    const candidate = mockDb.users.find((u) => u.username === username);
    if (!candidate || candidate.status !== 'ACTIVE' || password !== MOCK_SIMULATION_PASSWORD) {
      return makeErrorResponse('AUTH_INVALID_CREDENTIALS');
    }

    mockDb.currentUserId = candidate.id;
    candidate.last_login_at = new Date().toISOString();
    mockDb.csrfToken = `csrf-sim-${candidate.username}-${Date.now().toString(36)}`;

    appendMockAuditEvent({
      actor: candidate,
      action: 'AUTH_LOGIN',
      entityType: 'user_accounts',
      entityId: candidate.id,
      summary: `Login simulasi berhasil untuk ${candidate.username}`,
    });

    return makeSimpleEnvelope(candidate);
  }),

  http.post('/api/v1/auth/logout', ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) {
      return csrfError;
    }
    const currentUser = getAuthenticatedMockUser();
    mockDb.currentUserId = null;
    mockDb.csrfToken = `csrf-sim-anon-${Date.now().toString(36)}`;
    appendMockAuditEvent({
      actor: currentUser,
      action: 'AUTH_LOGOUT',
      entityType: 'user_accounts',
      entityId: currentUser?.id ?? null,
      summary: 'Sesi diakhiri oleh pengguna',
    });
    return makeSimpleEnvelope(null);
  }),

  http.get('/api/v1/auth/me', () => {
    const user = getAuthenticatedMockUser();
    if (!user) {
      return makeErrorResponse('AUTH_REQUIRED');
    }
    return makeSimpleEnvelope(user);
  }),
];
