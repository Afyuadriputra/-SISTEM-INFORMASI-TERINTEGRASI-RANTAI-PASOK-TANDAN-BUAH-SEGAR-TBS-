import Decimal from 'decimal.js';
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
  withMockIdempotency,
} from '../utils';

export const receivingHandlers = [
  http.get('/api/v1/receipts', ({ request }) => {
    const auth = requireMockPermission('receipts.read');
    if ('error' in auth) return auth.error;

    const url = new URL(request.url);
    const status = (url.searchParams.get('status') ?? '').trim();
    const coopScope = auth.user.access_scopes.find((s) => s.scope_type === 'COOPERATIVE')?.cooperative_id;
    const farmerScope = auth.user.access_scopes.find((s) => s.scope_type === 'FARMER')?.farmer_id;

    let items = mockDb.tbsReceipts;
    if (coopScope) {
      items = items.filter((r) => r.cooperative_id === coopScope);
    }
    if (farmerScope) {
      items = items.filter((r) => r.farmer_id === farmerScope);
    }
    if (status) {
      items = items.filter((r) => r.status === status);
    }
    return makePaginatedEnvelope(items, url);
  }),

  http.post('/api/v1/receipts', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('receipts.create');
    if ('error' in auth) return auth.error;

    return withMockIdempotency(request, 'createReceiptDraft', async () => {
      const body = (await request.json().catch(() => null)) as
        | components['schemas']['CreateReceiptRequest']
        | null;
      if (!body?.farmer_id || !body?.farm_id || !body?.received_at) {
        throw { errorResponse: makeErrorResponse('VAL_REQUIRED_FIELD') };
      }

      const farmer = mockDb.farmers.find((f) => f.id === body.farmer_id);
      const farm = mockDb.farms.find((fm) => fm.id === body.farm_id);
      if (!farmer || !farm) {
        return {
          status: 404,
          data: null,
        };
      }

      const coopScope = auth.user.access_scopes.find(
        (s) => s.scope_type === 'COOPERATIVE',
      )?.cooperative_id;
      const now = new Date().toISOString();
      const seqNum = String(mockDb.tbsReceipts.length + 101).padStart(4, '0');
      const created: components['schemas']['TbsReceipt'] = {
        id: `50000000-0000-4000-8000-${String(mockDb.tbsReceipts.length + 10).padStart(12, '0')}`,
        receipt_number: `RCP-2026-${seqNum}`,
        farmer_id: farmer.id,
        farmer_name: farmer.full_name,
        farm_id: farm.id,
        farm_name: farm.farm_name,
        cooperative_id: coopScope ?? farmer.cooperative_id,
        harvest_date: body.harvest_date ?? null,
        received_at: body.received_at,
        status: 'DRAFT',
        current_weighing: null,
        net_weight_after_grading_kg: null,
        weighing_revisions: [],
        grading_items: [],
        version: 1,
        created_at: now,
        updated_at: now,
      };
      mockDb.tbsReceipts.unshift(created);
      appendMockAuditEvent({
        actor: auth.user,
        action: 'RECEIPT_CREATED',
        entityType: 'tbs_receipts',
        entityId: created.id,
        summary: `Penerimaan TBS dibuat: ${created.receipt_number}`,
      });
      return { status: 201, data: created };
    }).catch((err: { errorResponse?: Response }) => {
      if (err?.errorResponse) return err.errorResponse;
      return makeErrorResponse('SYS_INTERNAL_ERROR');
    });
  }),

  http.get('/api/v1/receipts/:receiptId', ({ params }) => {
    const auth = requireMockPermission('receipts.read');
    if ('error' in auth) return auth.error;
    const item = mockDb.tbsReceipts.find((r) => r.id === String(params.receiptId));
    if (!item) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    return makeSimpleEnvelope(item);
  }),

  http.post('/api/v1/receipts/:receiptId/weighing', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('receipts.weigh');
    if ('error' in auth) return auth.error;

    const idx = mockDb.tbsReceipts.findIndex((r) => r.id === String(params.receiptId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.tbsReceipts[idx];

    if (['ALLOCATED', 'SHIPPED', 'CLOSED', 'CANCELLED'].includes(current.status)) {
      return makeErrorResponse('TBS_RECEIPT_LOCKED');
    }

    const body = (await request.json().catch(() => null)) as
      | components['schemas']['RecordWeighingRequest']
      | null;
    if (!body || typeof body.version !== 'number') return makeErrorResponse('VAL_REQUIRED_FIELD');
    if (body.version !== current.version) return makeErrorResponse('TBS_STALE_RECORD_VERSION');

    const gross = new Decimal(body.gross_weight_kg);
    const tare = new Decimal(body.tare_weight_kg);
    if (gross.isNegative() || tare.isNegative() || tare.greaterThan(gross)) {
      return makeErrorResponse('TBS_INVALID_WEIGHT');
    }
    if (current.status === 'VALIDATED' && (!body.correction_reason || body.correction_reason.trim().length < 3)) {
      return makeErrorResponse('VAL_REQUIRED_FIELD', {
        message: 'Alasan koreksi wajib diisi untuk mengubah berat penerimaan yang sudah divalidasi (BR-011).',
      });
    }

    const netto = gross.minus(tare).toFixed(3);
    const revNum = (current.weighing_revisions?.length ?? 0) + 1;
    const newRev: components['schemas']['ReceiptWeighingRevision'] = {
      id: `50000000-0000-4000-8000-${Date.now().toString().slice(-12)}`,
      revision_number: revNum,
      gross_weight_kg: gross.toFixed(3),
      tare_weight_kg: tare.toFixed(3),
      net_weight_kg: netto,
      weighed_at: new Date().toISOString(),
      weighed_by: auth.user.id,
      is_current: true,
      correction_reason: body.correction_reason ?? null,
    };

    const prevRevs = (current.weighing_revisions ?? []).map((r) => ({ ...r, is_current: false }));
    const updated: components['schemas']['TbsReceipt'] = {
      ...current,
      current_weighing: newRev,
      net_weight_after_grading_kg: netto,
      weighing_revisions: [newRev, ...prevRevs],
      version: current.version + 1,
      updated_at: new Date().toISOString(),
    };
    mockDb.tbsReceipts[idx] = updated;
    return makeSimpleEnvelope(updated);
  }),

  http.post('/api/v1/receipts/:receiptId/grading', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('receipts.weigh');
    if ('error' in auth) return auth.error;

    const idx = mockDb.tbsReceipts.findIndex((r) => r.id === String(params.receiptId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.tbsReceipts[idx];
    if (['ALLOCATED', 'SHIPPED', 'CLOSED', 'CANCELLED'].includes(current.status)) {
      return makeErrorResponse('TBS_RECEIPT_LOCKED');
    }
    if (!current.current_weighing) {
      return makeErrorResponse('TBS_INVALID_STATE_TRANSITION', {
        message: 'Penimbangan Bruto & Tara wajib dicatat sebelum grading.',
      });
    }

    const body = (await request.json().catch(() => null)) as
      | components['schemas']['RecordGradingRequest']
      | null;
    if (!body || !Array.isArray(body.items) || body.items.length === 0) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }
    if (body.version !== current.version) return makeErrorResponse('TBS_STALE_RECORD_VERSION');

    const baseNetto = new Decimal(current.current_weighing.net_weight_kg);
    let totalDedKg = new Decimal(0);
    const items: components['schemas']['ReceiptGradingItem'][] = [];

    for (const item of body.items) {
      const val = new Decimal(item.deduction_value);
      if (val.isNegative() || (item.deduction_type === 'WEIGHT_PERCENT' && val.greaterThan(100))) {
        return makeErrorResponse('TBS_INVALID_GRADING_DEDUCTION');
      }
      const dedKg =
        item.deduction_type === 'WEIGHT_PERCENT'
          ? baseNetto.times(val).div(100)
          : item.deduction_type === 'WEIGHT_KG'
            ? val
            : new Decimal(0);
      totalDedKg = totalDedKg.plus(dedKg);
      items.push({
        id: `50000000-0000-4000-8000-${Date.now().toString().slice(-12)}`,
        grading_category: item.grading_category,
        measurement_value: new Decimal(item.measurement_value).toFixed(4),
        deduction_type: item.deduction_type,
        deduction_value: val.toFixed(4),
        deduction_weight_kg: dedKg.toFixed(3),
        deduction_amount: item.deduction_type === 'VALUE_AMOUNT' ? val.toFixed(2) : null,
        calculation_basis: item.calculation_basis,
        is_simulation: true,
        notes: item.notes ?? null,
      });
    }

    if (totalDedKg.greaterThan(baseNetto)) {
      return makeErrorResponse('TBS_INVALID_GRADING_DEDUCTION');
    }

    const updated: components['schemas']['TbsReceipt'] = {
      ...current,
      grading_items: items,
      net_weight_after_grading_kg: baseNetto.minus(totalDedKg).toFixed(3),
      version: current.version + 1,
      updated_at: new Date().toISOString(),
    };
    mockDb.tbsReceipts[idx] = updated;
    return makeSimpleEnvelope(updated);
  }),

  http.post('/api/v1/receipts/:receiptId/validate', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('receipts.validate');
    if ('error' in auth) return auth.error;

    const idx = mockDb.tbsReceipts.findIndex((r) => r.id === String(params.receiptId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.tbsReceipts[idx];
    if (current.status !== 'DRAFT' || !current.current_weighing) {
      return makeErrorResponse('TBS_INVALID_STATE_TRANSITION');
    }

    const body = (await request.json().catch(() => null)) as { version?: number } | null;
    if (body && typeof body.version === 'number' && body.version !== current.version) {
      return makeErrorResponse('TBS_STALE_RECORD_VERSION');
    }

    const updated: components['schemas']['TbsReceipt'] = {
      ...current,
      status: 'VALIDATED',
      version: current.version + 1,
      updated_at: new Date().toISOString(),
    };
    mockDb.tbsReceipts[idx] = updated;
    return makeSimpleEnvelope(updated);
  }),

  http.post('/api/v1/receipts/:receiptId/cancel', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('receipts.cancel');
    if ('error' in auth) return auth.error;

    const idx = mockDb.tbsReceipts.findIndex((r) => r.id === String(params.receiptId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.tbsReceipts[idx];
    if (['ALLOCATED', 'SHIPPED', 'CLOSED', 'CANCELLED'].includes(current.status)) {
      return makeErrorResponse('TBS_RECEIPT_LOCKED');
    }

    const body = (await request.json().catch(() => null)) as { reason?: string; version?: number } | null;
    if (!body?.reason || body.reason.trim().length < 3) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }

    const updated: components['schemas']['TbsReceipt'] = {
      ...current,
      status: 'CANCELLED',
      version: current.version + 1,
      updated_at: new Date().toISOString(),
    };
    mockDb.tbsReceipts[idx] = updated;
    appendMockAuditEvent({
      actor: auth.user,
      action: 'RECEIPT_CANCELLED',
      entityType: 'tbs_receipts',
      entityId: updated.id,
      summary: `Penerimaan ${updated.receipt_number} dibatalkan: ${body.reason}`,
    });
    return makeSimpleEnvelope(updated);
  }),
];
