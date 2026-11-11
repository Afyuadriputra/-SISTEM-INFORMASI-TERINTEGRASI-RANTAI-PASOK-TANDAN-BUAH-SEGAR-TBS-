import { HttpResponse } from 'msw';
import type { components } from '@/lib/api/generated';
import type { AuthenticatedUser } from '@/lib/auth/permissions';
import { ERROR_CATALOG, type ErrorCode } from '@/lib/errors/errorCatalog';
import { mockDb } from './mockDb';

let reqSeq = 1;

export function nextRequestId(): string {
  const id = `req-mock-${String(reqSeq).padStart(4, '0')}`;
  reqSeq += 1;
  return id;
}

export function makeSimpleEnvelope<TData>(
  data: TData,
  metaOverrides?: Partial<components['schemas']['SimpleSuccessMeta']>,
  status = 200,
) {
  const requestId = nextRequestId();
  return HttpResponse.json(
    {
      success: true,
      data,
      meta: {
        data_freshness_at: new Date().toISOString(),
        simulation_notice: 'Mode simulasi MSW aktif (bukan transaksi produksi Perumda).',
        idempotency_replayed: null,
        ...metaOverrides,
      },
      request_id: requestId,
    },
    {
      status,
      headers: { 'X-Request-Id': requestId },
    },
  );
}

export function paginate<TItem>(items: readonly TItem[], requestUrl: URL) {
  const page = Math.max(1, Number(requestUrl.searchParams.get('page') ?? '1') || 1);
  const pageSize = Math.min(
    100,
    Math.max(1, Number(requestUrl.searchParams.get('page_size') ?? '20') || 20),
  );
  const totalItems = items.length;
  const totalPages = totalItems === 0 ? 0 : Math.ceil(totalItems / pageSize);
  const start = (page - 1) * pageSize;
  const sliced = items.slice(start, start + pageSize);

  return {
    items: sliced,
    meta: {
      page,
      page_size: pageSize,
      total_items: totalItems,
      total_pages: totalPages,
      has_next: page < totalPages,
      has_prev: page > 1,
      data_freshness_at: new Date().toISOString(),
      simulation_notice: 'Mode simulasi MSW aktif (bukan transaksi produksi Perumda).',
    } satisfies components['schemas']['PaginationMeta'],
  };
}

export function makePaginatedEnvelope<TItem>(allItems: readonly TItem[], requestUrl: URL) {
  const { items, meta } = paginate(allItems, requestUrl);
  const requestId = nextRequestId();
  return HttpResponse.json(
    {
      success: true,
      data: items,
      meta,
      request_id: requestId,
    },
    {
      status: 200,
      headers: { 'X-Request-Id': requestId },
    },
  );
}

export function makeErrorResponse(
  code: ErrorCode,
  options?: { status?: number; message?: string; details?: unknown },
) {
  const entry = ERROR_CATALOG[code];
  const status = options?.status ?? entry.httpStatus;
  const requestId = nextRequestId();
  return HttpResponse.json(
    {
      success: false,
      error: {
        code,
        message: options?.message ?? entry.message,
        details: options?.details ?? null,
      },
      request_id: requestId,
    },
    {
      status,
      headers: { 'X-Request-Id': requestId },
    },
  );
}

export function getAuthenticatedMockUser(): AuthenticatedUser | null {
  if (!mockDb.currentUserId) {
    return null;
  }
  const user = mockDb.users.find((u) => u.id === mockDb.currentUserId) ?? null;
  if (!user || user.status !== 'ACTIVE') {
    mockDb.currentUserId = null;
    return null;
  }
  return user;
}

export function assertMockCsrf(request: Request): Response | null {
  const token = request.headers.get('X-CSRF-Token');
  if (!token || token !== mockDb.csrfToken) {
    return makeErrorResponse('AUTH_CSRF_INVALID');
  }
  return null;
}

export function requireMockPermission(
  permission: string,
): { user: AuthenticatedUser } | { error: Response } {
  const user = getAuthenticatedMockUser();
  if (!user) {
    return { error: makeErrorResponse('AUTH_REQUIRED') };
  }
  if (!user.permissions.includes(permission)) {
    return { error: makeErrorResponse('AUTH_ACCESS_DENIED') };
  }
  return { user };
}

export async function withMockIdempotency(
  request: Request,
  operationKey: string,
  handler: () => Promise<{ status: number; data: unknown; metaOverrides?: Record<string, unknown> }> | {
    status: number;
    data: unknown;
    metaOverrides?: Record<string, unknown>;
  },
): Promise<Response> {
  const idemKey = request.headers.get('Idempotency-Key');
  if (!idemKey || !/^[A-Za-z0-9._:-]{8,128}$/.test(idemKey)) {
    return makeErrorResponse('VAL_REQUIRED_FIELD', {
      message: 'Header Idempotency-Key wajib diisi dengan format yang sah.',
    });
  }

  const rawBody = await request.clone().text();
  const compositeKey = `${operationKey}:${mockDb.currentUserId ?? 'anon'}:${idemKey}`;
  const existing = mockDb.idempotencyStore.get(compositeKey);
  if (existing) {
    if (existing.payloadSignature !== rawBody) {
      return makeErrorResponse('IDM_KEY_CONFLICT_PAYLOAD_MISMATCH');
    }
    const requestId = nextRequestId();
    return HttpResponse.json(
      {
        ...(existing.body as Record<string, unknown>),
        meta: {
          ...((existing.body as { meta?: Record<string, unknown> }).meta ?? {}),
          idempotency_replayed: true,
        },
        request_id: requestId,
      },
      { status: existing.status, headers: { 'X-Request-Id': requestId } },
    );
  }

  const result = await handler();
  const requestId = nextRequestId();
  const envelope = {
    success: true,
    data: result.data,
    meta: {
      data_freshness_at: new Date().toISOString(),
      simulation_notice: 'Mode simulasi MSW aktif (bukan transaksi produksi Perumda).',
      idempotency_replayed: false,
      ...result.metaOverrides,
    },
    request_id: requestId,
  };

  mockDb.idempotencyStore.set(compositeKey, {
    payloadSignature: rawBody,
    status: result.status,
    body: envelope,
  });

  return HttpResponse.json(envelope, {
    status: result.status,
    headers: { 'X-Request-Id': requestId },
  });
}

export function appendMockAuditEvent(params: {
  actor: AuthenticatedUser | null;
  action: string;
  entityType: string;
  entityId: string | null;
  summary: string;
}): void {
  mockDb.auditEvents.unshift({
    id: `aud-mock-${Date.now()}-${mockDb.auditEvents.length + 1}`,
    actor_user_id: params.actor?.id ?? null,
    actor_username: params.actor?.username ?? 'system',
    action: params.action,
    entity_type: params.entityType,
    entity_id: params.entityId,
    request_id: nextRequestId(),
    summary: params.summary,
    created_at: new Date().toISOString(),
  });
}
