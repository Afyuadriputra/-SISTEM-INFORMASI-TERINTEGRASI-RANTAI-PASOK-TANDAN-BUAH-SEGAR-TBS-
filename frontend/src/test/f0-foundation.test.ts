import { http, HttpResponse } from 'msw';
import { describe, expect, it, vi } from 'vitest';
import { apiRequest, clearCsrfToken, getCachedCsrfToken, setUnauthorizedHandler } from '@/lib/api/client';
import {
  CANONICAL_ROUTES,
  canAccessRoutePath,
  getRoleHomePath,
  isNonApproverAdmin,
} from '@/lib/auth/permissions';
import { loginWithCredentials, logoutSession } from '@/lib/auth/session';
import { assertStrictRealModeNoMockFallback, getFrontendConfig } from '@/lib/config/env';
import {
  computeNettoPreview,
  computeReconciliationDiffPreview,
  formatCalendarOrWibDate,
  formatHectares,
  formatIdr,
  formatKg,
  formatPercent,
  formatPricePerKg,
  formatWibDateTime,
  parseDecimalStrict,
} from '@/lib/decimal/precision';
import {
  ApiError,
  ERROR_CATALOG,
  extractFieldErrors,
  getSafeErrorMessage,
} from '@/lib/errors/errorCatalog';
import { useUiStore } from '@/lib/state/uiStore';
import { MOCK_SIMULATION_PASSWORD } from '@/mocks/mockDb';
import { server } from '@/mocks/server';

describe('F0 Foundation: Config, Decimal Precision & Error Catalog', () => {
  it('validates environment config strictly without silent real-mode fallback', () => {
    expect(getFrontendConfig({}).apiMode).toBe('mock');
    expect(getFrontendConfig({ VITE_API_MODE: 'real', VITE_API_BASE_URL: 'http://127.0.0.1:8000/' })).toEqual({
      apiMode: 'real',
      apiBaseUrl: 'http://127.0.0.1:8000',
      appName: 'AgroNiaga TBS - Perumda Tuah Sekata',
    });
    expect(() => getFrontendConfig({ VITE_API_MODE: 'invalid' })).toThrow();
    expect(() => assertStrictRealModeNoMockFallback()).not.toThrow();
  });

  it('formats decimal precision exactly with zero float drift and WIB timestamps', () => {
    expect(parseDecimalStrict('2450,500')?.toFixed(3)).toBe('2450.500');
    expect(parseDecimalStrict('0.1')?.plus(parseDecimalStrict('0.2')!).toFixed(1)).toBe('0.3');
    expect(formatKg('2450.5')).toBe('2.450,500 kg');
    expect(formatPricePerKg('2850.5')).toBe('Rp 2.850,50/kg');
    expect(formatIdr('12500000.75')).toBe('Rp 12.500.000,75');
    expect(formatPercent('1.5')).toBe('1,5000%');
    expect(formatHectares('2.375')).toBe('2,3750 ha');

    const nettoOk = computeNettoPreview('5000.000', '1850.250');
    expect(nettoOk.valid).toBe(true);
    expect(nettoOk.nettoString).toBe('3149.750');

    const nettoBad = computeNettoPreview('1000', '1500');
    expect(nettoBad.valid).toBe(false);
    expect(nettoBad.errorMessage).toContain('melebihi berat bruto');

    const diffNeg = computeReconciliationDiffPreview('10000.000', '10050.000', '1.5000');
    expect(diffNeg?.isNegativeDifference).toBe(true);
    expect(diffNeg?.exceedsTolerance).toBe(true);

    expect(formatCalendarOrWibDate('2026-11-10')).toBe('10 Nov 2026');
    expect(formatWibDateTime('2026-11-10T01:30:00Z')).toContain('WIB');
  });

  it('exposes all 69 canonical contract error codes and parses field validation details', () => {
    expect(Object.keys(ERROR_CATALOG)).toHaveLength(69);
    expect(getSafeErrorMessage('AUTH_CONFLICT_OF_DUTIES')).toContain('berbeda');
    expect(
      extractFieldErrors([
        { loc: ['body', 'tare_weight_kg'], msg: 'Tara melebihi bruto' },
        { field: 'latitude', message: 'Koordinat tidak sah' },
      ]),
    ).toEqual({
      tare_weight_kg: 'Tara melebihi bruto',
      latitude: 'Koordinat tidak sah',
    });
  });

  it('enforces all 26 AFD §36 canonical routes and role permissions including BR-SYS-002', () => {
    expect(CANONICAL_ROUTES).toHaveLength(26);
    expect(getRoleHomePath(null)).toBe('/login');

    const adminUser = {
      id: '1',
      username: 'sim_sys_admin_01',
      display_name: 'Admin',
      status: 'ACTIVE' as const,
      roles: ['SYSTEM_ADMIN' as const],
      access_scopes: [],
      permissions: ['admin.users.read'],
      last_login_at: null,
      non_approver_admin: true,
    };
    expect(isNonApproverAdmin(adminUser)).toBe(true);
    expect(getRoleHomePath(adminUser)).toBe('/app/admin');
    expect(canAccessRoutePath(adminUser, '/app/admin/audit')).toBe(true);
    expect(canAccessRoutePath(adminUser, '/app/direksi/persetujuan')).toBe(false);
    expect(canAccessRoutePath(null, '/harga-tbs')).toBe(true);
    expect(canAccessRoutePath(null, '/app/perumda')).toBe(false);
  });
});

describe('F0 Foundation: API Client, CSRF, Idempotency & MSW Integration', () => {
  it('bootstraps CSRF, logs in, reads current session, and wipes CSRF on logout', async () => {
    const user = await loginWithCredentials({
      username: 'sim_perumda_ops_01',
      password: MOCK_SIMULATION_PASSWORD,
    });
    expect(user.username).toBe('sim_perumda_ops_01');
    expect(getCachedCsrfToken()).not.toBeNull();

    const pricesEnv = await apiRequest<{ success: true; data: unknown[] }>({
      path: '/api/v1/public/prices',
    });
    expect(pricesEnv.success).toBe(true);
    expect(pricesEnv.data.length).toBeGreaterThan(0);

    await logoutSession();
    expect(getCachedCsrfToken()).toBeNull();
  });

  it('retries once automatically when 403 AUTH_CSRF_INVALID is returned', async () => {
    let attempts = 0;
    server.use(
      http.post('/api/v1/test-csrf-retry', ({ request }) => {
        attempts += 1;
        if (attempts === 1) {
          return HttpResponse.json(
            {
              success: false,
              error: { code: 'AUTH_CSRF_INVALID', message: 'Stale token', details: null },
              request_id: 'req-csrf-1',
            },
            { status: 403 },
          );
        }
        return HttpResponse.json({
          success: true,
          data: { tokenSeen: request.headers.get('X-CSRF-Token') },
          meta: { data_freshness_at: null, simulation_notice: null, idempotency_replayed: null },
          request_id: 'req-csrf-2',
        });
      }),
    );

    const res = await apiRequest<{ success: true; data: { tokenSeen: string } }>({
      path: '/api/v1/test-csrf-retry',
      method: 'POST',
      body: { ping: true },
    });
    expect(attempts).toBe(2);
    expect(res.data.tokenSeen).toBe('csrf-sim-agroniaga-token');
  });

  it('invokes unauthorized handler on 401 and reuses per-action Idempotency-Key safely', async () => {
    const onUnauth = vi.fn();
    setUnauthorizedHandler(onUnauth);
    clearCsrfToken();

    await expect(
      apiRequest({
        path: '/api/v1/auth/me',
        method: 'GET',
      }),
    ).rejects.toBeInstanceOf(ApiError);
    expect(onUnauth).toHaveBeenCalledTimes(1);
    setUnauthorizedHandler(null);

    const k1 = useUiStore.getState().getOrCreateActionIdempotencyKey('do:issue:1');
    const k2 = useUiStore.getState().getOrCreateActionIdempotencyKey('do:issue:1');
    expect(k1).toBe(k2);
    expect(k1).toMatch(/^[A-Za-z0-9._:-]{8,128}$/);
  });
});
