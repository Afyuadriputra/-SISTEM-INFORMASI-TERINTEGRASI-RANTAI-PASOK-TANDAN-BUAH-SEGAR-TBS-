import { http } from 'msw';
import type { components } from '@/lib/api/generated';
import { mockDb } from '../mockDb';
import {
  appendMockAuditEvent,
  assertMockCsrf,
  makeErrorResponse,
  makePaginatedEnvelope,
  makeSimpleEnvelope,
  requireMockPermission,
} from '../utils';

type InternalPriceQuote = components['schemas']['InternalPriceQuote'];

function toInternalPriceQuote(q: (typeof mockDb.millPriceQuotes)[number]): InternalPriceQuote {
  const now = Date.now();
  const expired =
    q.status === 'PUBLISHED' && q.effective_until
      ? new Date(q.effective_until).getTime() < now
      : false;
  return {
    id: q.id,
    mill_id: q.mill_id,
    mill_name: q.mill_name,
    mill_code: q.mill_code,
    regency: q.regency,
    price_category_id: q.price_category_id,
    price_category_code: q.price_category_code,
    price_category_name: q.price_category_name,
    unit: q.unit,
    source_id: q.source_id,
    source_name: q.source_name,
    source_type: q.source_type as InternalPriceQuote['source_type'],
    price_per_kg: q.price_per_kg,
    effective_from: q.effective_from,
    effective_until: q.effective_until,
    status: q.status as InternalPriceQuote['status'],
    display_status: expired ? 'EXPIRED' : (q.status as InternalPriceQuote['display_status']),
    is_expired: expired,
    submitted_by: q.submitted_by,
    verified_by: q.verified_by ?? null,
    verified_at: q.verified_at ?? null,
    published_at: q.published_at ?? null,
    source_document_id: q.source_document_id ?? null,
    notes: q.notes ?? null,
    version: q.version,
    is_simulation: q.is_simulation,
    created_at: q.created_at,
    updated_at: q.updated_at,
    verification_events: [],
  };
}

export const pricingHandlers = [
  http.get('/api/v1/prices/reference-meta', () => {
    const auth = requireMockPermission('prices.read');
    if ('error' in auth) return auth.error;
    return makeSimpleEnvelope({
      sources: mockDb.priceSources,
      categories: mockDb.priceCategories,
    });
  }),

  http.get('/api/v1/prices', ({ request }) => {
    const auth = requireMockPermission('prices.read');
    if ('error' in auth) return auth.error;
    const url = new URL(request.url);
    const status = (url.searchParams.get('status') ?? '').trim();
    const millId = (url.searchParams.get('mill_id') ?? '').trim();
    const search = (url.searchParams.get('search') ?? '').trim().toLowerCase();

    let items = mockDb.millPriceQuotes.map(toInternalPriceQuote);
    if (status) {
      items = items.filter((item) => item.status === status || item.display_status === status);
    }
    if (millId) {
      items = items.filter((item) => item.mill_id === millId);
    }
    if (search) {
      items = items.filter(
        (item) =>
          item.mill_name.toLowerCase().includes(search) ||
          (item.mill_code ?? '').toLowerCase().includes(search) ||
          (item.price_category_name ?? '').toLowerCase().includes(search),
      );
    }
    return makePaginatedEnvelope(items, url);
  }),

  http.post('/api/v1/prices', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('prices.create');
    if ('error' in auth) return auth.error;

    const body = (await request.json().catch(() => null)) as
      | components['schemas']['CreatePriceDraftRequest']
      | null;
    if (!body?.mill_id || !body?.price_category_id || !body?.source_id || !body?.price_per_kg || !body?.effective_from) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }
    if (Number(body.price_per_kg) <= 0 || !Number.isFinite(Number(body.price_per_kg))) {
      return makeErrorResponse('PRICE_INVALID_AMOUNT');
    }
    if (body.effective_until && Date.parse(body.effective_until) <= Date.parse(body.effective_from)) {
      return makeErrorResponse('PRICE_INVALID_PERIOD');
    }

    const mill = mockDb.mills.find((m) => m.id === body.mill_id);
    const cat = mockDb.priceCategories.find((c) => c.id === body.price_category_id);
    const src = mockDb.priceSources.find((s) => s.id === body.source_id);
    if (!mill || !cat || !src) {
      return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    }

    const now = new Date().toISOString();
    const newQuote = {
      id: `60000000-0000-4000-8000-${String(mockDb.millPriceQuotes.length + 201).padStart(12, '0')}`,
      mill_id: mill.id,
      mill_name: mill.mill_name,
      mill_code: mill.mill_code,
      regency: mill.regency,
      price_category_id: cat.id,
      price_category_code: cat.category_code,
      price_category_name: cat.name,
      unit: 'IDR/kg',
      source_id: src.id,
      source_name: src.source_name,
      source_type: src.source_type,
      price_per_kg: Number(body.price_per_kg).toFixed(2),
      effective_from: body.effective_from,
      effective_until: body.effective_until ?? null,
      status: 'DRAFT',
      display_status: 'DRAFT',
      is_expired: false,
      submitted_by: auth.user.id,
      verified_by: null,
      verified_at: null,
      published_at: null,
      updated_at: now,
      source_document_id: body.source_document_id ?? null,
      notes: body.notes ?? null,
      version: 1,
      is_simulation: true,
      created_at: now,
    };
    mockDb.millPriceQuotes.unshift(newQuote as unknown as (typeof mockDb.millPriceQuotes)[number]);
    appendMockAuditEvent({
      actor: auth.user,
      action: 'PRICE_DRAFT_CREATED',
      entityType: 'mill_price_quotes',
      entityId: newQuote.id,
      summary: `Draf harga dibuat untuk ${mill.mill_code} (${newQuote.price_per_kg} Rp/kg)`,
    });
    return makeSimpleEnvelope(toInternalPriceQuote(newQuote as unknown as (typeof mockDb.millPriceQuotes)[number]), undefined, 201);
  }),

  http.get('/api/v1/prices/:priceQuoteId', ({ params }) => {
    const auth = requireMockPermission('prices.read');
    if ('error' in auth) return auth.error;
    const item = mockDb.millPriceQuotes.find((q) => q.id === String(params.priceQuoteId));
    if (!item) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    return makeSimpleEnvelope(toInternalPriceQuote(item));
  }),

  http.patch('/api/v1/prices/:priceQuoteId', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('prices.create');
    if ('error' in auth) return auth.error;
    const idx = mockDb.millPriceQuotes.findIndex((q) => q.id === String(params.priceQuoteId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.millPriceQuotes[idx];
    const body = (await request.json().catch(() => null)) as
      | components['schemas']['UpdatePriceDraftRequest']
      | null;
    if (!body || typeof body.version !== 'number') return makeErrorResponse('VAL_REQUIRED_FIELD');
    if (body.version !== current.version) return makeErrorResponse('MD_STALE_RECORD_VERSION');
    if (current.status !== 'DRAFT' && current.status !== 'REJECTED') {
      return makeErrorResponse('PRICE_INVALID_STATE_TRANSITION');
    }
    const updated = {
      ...current,
      price_per_kg: body.price_per_kg ? Number(body.price_per_kg).toFixed(2) : current.price_per_kg,
      effective_from: body.effective_from ?? current.effective_from,
      effective_until: body.effective_until !== undefined ? body.effective_until : current.effective_until,
      notes: body.notes !== undefined ? body.notes : current.notes,
      version: current.version + 1,
      updated_at: new Date().toISOString(),
    };
    mockDb.millPriceQuotes[idx] = updated;
    return makeSimpleEnvelope(toInternalPriceQuote(updated));
  }),

  http.post('/api/v1/prices/:priceQuoteId/submit', ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('prices.submit');
    if ('error' in auth) return auth.error;
    const idx = mockDb.millPriceQuotes.findIndex((q) => q.id === String(params.priceQuoteId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.millPriceQuotes[idx];
    if (current.status !== 'DRAFT' && current.status !== 'REJECTED') {
      return makeErrorResponse('PRICE_INVALID_STATE_TRANSITION');
    }
    const updated = {
      ...current,
      status: 'PENDING_VERIFICATION',
      display_status: 'PENDING_VERIFICATION',
      submitted_by: auth.user.id,
      version: current.version + 1,
      updated_at: new Date().toISOString(),
    };
    mockDb.millPriceQuotes[idx] = updated as (typeof mockDb.millPriceQuotes)[number];
    return makeSimpleEnvelope(toInternalPriceQuote(updated as (typeof mockDb.millPriceQuotes)[number]));
  }),

  http.post('/api/v1/prices/:priceQuoteId/verify', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('prices.verify');
    if ('error' in auth) return auth.error;
    if (auth.user.non_approver_admin) return makeErrorResponse('AUTH_OPERATION_FORBIDDEN');

    const idx = mockDb.millPriceQuotes.findIndex((q) => q.id === String(params.priceQuoteId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.millPriceQuotes[idx];
    if (current.status !== 'PENDING_VERIFICATION') {
      return makeErrorResponse('PRICE_INVALID_STATE_TRANSITION');
    }
    if (current.submitted_by === auth.user.id) {
      return makeErrorResponse('AUTH_CONFLICT_OF_DUTIES');
    }

    const body = (await request.json().catch(() => null)) as
      | components['schemas']['VerifyPriceRequest']
      | null;
    if (!body?.decision) return makeErrorResponse('VAL_REQUIRED_FIELD');
    if (body.decision === 'REJECT' && (!body.reason || body.reason.trim().length < 3)) {
      return makeErrorResponse('VAL_REQUIRED_FIELD', {
        message: 'Alasan penolakan harga wajib diisi.',
      });
    }

    const nextStatus = body.decision === 'APPROVE' ? 'VERIFIED' : 'REJECTED';
    const now = new Date().toISOString();
    const updated = {
      ...current,
      status: nextStatus,
      display_status: nextStatus,
      verified_by: auth.user.id,
      verified_at: now,
      notes: body.reason ?? current.notes,
      version: current.version + 1,
      updated_at: now,
    };
    mockDb.millPriceQuotes[idx] = updated as (typeof mockDb.millPriceQuotes)[number];
    appendMockAuditEvent({
      actor: auth.user,
      action: body.decision === 'APPROVE' ? 'PRICE_VERIFIED' : 'PRICE_REJECTED',
      entityType: 'mill_price_quotes',
      entityId: current.id,
      summary: `Harga ${current.mill_code} ${nextStatus}: ${body.reason ?? 'Disetujui checker'}`,
    });
    return makeSimpleEnvelope(toInternalPriceQuote(updated as (typeof mockDb.millPriceQuotes)[number]));
  }),

  http.post('/api/v1/prices/:priceQuoteId/publish', ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('prices.publish');
    if ('error' in auth) return auth.error;

    const idx = mockDb.millPriceQuotes.findIndex((q) => q.id === String(params.priceQuoteId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.millPriceQuotes[idx];
    if (current.status !== 'VERIFIED') {
      return makeErrorResponse('PRICE_NOT_VERIFIED');
    }

    const now = new Date().toISOString();
    const updated = {
      ...current,
      status: 'PUBLISHED',
      display_status: 'PUBLISHED',
      published_at: now,
      updated_at: now,
      version: current.version + 1,
    };
    mockDb.millPriceQuotes[idx] = updated as (typeof mockDb.millPriceQuotes)[number];
    appendMockAuditEvent({
      actor: auth.user,
      action: 'PRICE_PUBLISHED',
      entityType: 'mill_price_quotes',
      entityId: current.id,
      summary: `Harga ${current.mill_code} dipublikasikan (${current.price_per_kg})`,
    });
    return makeSimpleEnvelope(toInternalPriceQuote(updated as (typeof mockDb.millPriceQuotes)[number]));
  }),

  http.post('/api/v1/prices/:priceQuoteId/revoke', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('prices.revoke');
    if ('error' in auth) return auth.error;

    const idx = mockDb.millPriceQuotes.findIndex((q) => q.id === String(params.priceQuoteId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.millPriceQuotes[idx];
    const body = (await request.json().catch(() => null)) as { reason?: string } | null;
    if (!body?.reason || body.reason.trim().length < 3) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }
    const updated = {
      ...current,
      status: 'REVOKED',
      display_status: 'REVOKED',
      notes: body.reason,
      updated_at: new Date().toISOString(),
      version: current.version + 1,
    };
    mockDb.millPriceQuotes[idx] = updated as (typeof mockDb.millPriceQuotes)[number];
    return makeSimpleEnvelope(toInternalPriceQuote(updated as (typeof mockDb.millPriceQuotes)[number]));
  }),

  http.post('/api/v1/prices/disbun', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('prices.publish');
    if ('error' in auth) return auth.error;

    const body = (await request.json().catch(() => null)) as
      | components['schemas']['CreateDisbunPriceRequest']
      | null;
    if (!body?.price_source_id || !body?.price_category_id || !body?.price_per_kg || !body?.effective_from) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }
    const src = mockDb.priceSources.find((s) => s.id === body.price_source_id);
    const cat = mockDb.priceCategories.find((c) => c.id === body.price_category_id);
    if (!src || !cat) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');

    const created = {
      id: `60000000-0000-4000-8000-${String(mockDb.disbunReferencePrices.length + 501).padStart(12, '0')}`,
      source_name: src.source_name,
      category_code: cat.category_code,
      category_name: cat.name,
      age_group: cat.age_group ?? 'Umur 10-20 Tahun',
      price_per_kg: Number(body.price_per_kg).toFixed(2),
      effective_from: body.effective_from,
      effective_until: body.effective_until ?? null,
      verification_status: 'PUBLISHED' as const,
      created_at: new Date().toISOString(),
    };
    mockDb.disbunReferencePrices.unshift(created as (typeof mockDb.disbunReferencePrices)[number]);
    return makeSimpleEnvelope(created, undefined, 201);
  }),
];
