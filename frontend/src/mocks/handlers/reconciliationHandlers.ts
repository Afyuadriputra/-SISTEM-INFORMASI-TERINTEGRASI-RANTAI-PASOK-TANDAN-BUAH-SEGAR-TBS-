import Decimal from 'decimal.js';
import { http, HttpResponse } from 'msw';
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

export const reconciliationHandlers = [
  http.post('/api/v1/files', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('files.upload');
    if ('error' in auth) return auth.error;

    const formData = await request.formData().catch(() => null);
    const classification = String(formData?.get('classification') ?? 'MILL_TICKET_PROOF');
    const fileEntry = formData?.get('file');
    const filename =
      fileEntry && typeof fileEntry === 'object' && 'name' in fileEntry
        ? String((fileEntry as { name: string }).name)
        : 'bukti-unggah.pdf';
    const rawMime =
      fileEntry && typeof fileEntry === 'object' && 'type' in fileEntry && (fileEntry as { type: string }).type
        ? String((fileEntry as { type: string }).type)
        : 'application/pdf';
    const mimeType: components['schemas']['FileAsset']['mime_type'] =
      rawMime === 'image/jpeg' || rawMime === 'image/png' ? rawMime : 'application/pdf';

    const asset: components['schemas']['FileAsset'] = {
      id: `a0000000-0000-4000-8000-${String(mockDb.fileAssets.length + 911).padStart(12, '0')}`,
      original_filename: filename,
      mime_type: mimeType,
      size_bytes: 24576,
      checksum: `sha256-sim-${Date.now().toString(16)}`,
      classification: classification as components['schemas']['FileAsset']['classification'],
      uploaded_by: auth.user.id,
      created_at: new Date().toISOString(),
    };
    mockDb.fileAssets.unshift(asset);
    return makeSimpleEnvelope(asset, undefined, 201);
  }),

  http.get('/api/v1/files/:fileId', ({ params }) => {
    const auth = requireMockPermission('files.read');
    if ('error' in auth) return auth.error;
    const asset = mockDb.fileAssets.find((f) => f.id === String(params.fileId));
    if (!asset) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    return new HttpResponse(`Simulasi konten berkas ${asset.original_filename}`, {
      status: 200,
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Disposition': `attachment; filename="${asset.original_filename}"`,
      },
    });
  }),

  http.get('/api/v1/mill-tickets', ({ request }) => {
    const auth = requireMockPermission('mill_tickets.read');
    if ('error' in auth) return auth.error;
    const url = new URL(request.url);
    const millScope = auth.user.access_scopes.find((s) => s.scope_type === 'MILL')?.mill_id;
    let items = mockDb.millWeighingTickets;
    if (millScope) {
      items = items.filter((t) => t.mill_id === millScope);
    }
    return makePaginatedEnvelope(items, url);
  }),

  http.post('/api/v1/mill-tickets', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('mill_tickets.create');
    if ('error' in auth) return auth.error;

    return withMockIdempotency(request, 'createMillTicket', async () => {
      const body = (await request.json().catch(() => null)) as
        | components['schemas']['CreateMillTicketRequest']
        | null;
      if (!body?.delivery_order_id || !body?.ticket_number || !body?.gross_weight_kg || !body?.tare_weight_kg) {
        throw { errorResponse: makeErrorResponse('VAL_REQUIRED_FIELD') };
      }
      const deliveryOrder = mockDb.deliveryOrders.find((d) => d.id === body.delivery_order_id);
      if (!deliveryOrder) throw { errorResponse: makeErrorResponse('SYS_RESOURCE_NOT_FOUND') };

      const millScope = auth.user.access_scopes.find((s) => s.scope_type === 'MILL')?.mill_id;
      if (millScope && deliveryOrder.mill_id !== millScope) {
        throw { errorResponse: makeErrorResponse('MILL_EDO_MILL_MISMATCH') };
      }
      if (!['READY', 'IN_TRANSIT', 'ARRIVED', 'RECEIVED'].includes(deliveryOrder.status)) {
        throw { errorResponse: makeErrorResponse('MILL_EDO_NOT_ELIGIBLE') };
      }

      const dupCurrent = mockDb.millWeighingTickets.some(
        (t) =>
          t.is_current &&
          (t.delivery_order_id === deliveryOrder.id ||
            (t.mill_id === deliveryOrder.mill_id && t.ticket_number === body.ticket_number.trim())),
      );
      if (dupCurrent) {
        throw { errorResponse: makeErrorResponse('MILL_DUPLICATE_TICKET') };
      }

      const gross = new Decimal(body.gross_weight_kg);
      const tare = new Decimal(body.tare_weight_kg);
      if (gross.isNegative() || tare.isNegative() || tare.greaterThan(gross)) {
        throw { errorResponse: makeErrorResponse('TBS_INVALID_WEIGHT') };
      }

      const now = new Date().toISOString();
      const created: components['schemas']['MillWeighingTicket'] = {
        id: `80000000-0000-4000-8000-${String(mockDb.millWeighingTickets.length + 101).padStart(12, '0')}`,
        delivery_order_id: deliveryOrder.id,
        mill_id: deliveryOrder.mill_id,
        ticket_number: body.ticket_number.trim(),
        revision_number: 1,
        previous_ticket_id: null,
        gross_weight_kg: gross.toFixed(3),
        tare_weight_kg: tare.toFixed(3),
        net_weight_kg: gross.minus(tare).toFixed(3),
        weighed_at: body.weighed_at || now,
        verified_at: null,
        verified_by: null,
        is_current: true,
        status: 'DRAFT',
        proof_file_id: body.proof_file_id ?? null,
        correction_reason: null,
        grading_items: [],
        created_at: now,
      };
      mockDb.millWeighingTickets.unshift(created);
      return { status: 201, data: created };
    }).catch((err: { errorResponse?: Response }) => {
      if (err?.errorResponse) return err.errorResponse;
      return makeErrorResponse('SYS_INTERNAL_ERROR');
    });
  }),

  http.get('/api/v1/mill-tickets/:ticketId', ({ params }) => {
    const auth = requireMockPermission('mill_tickets.read');
    if ('error' in auth) return auth.error;
    const item = mockDb.millWeighingTickets.find((t) => t.id === String(params.ticketId));
    if (!item) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    return makeSimpleEnvelope(item);
  }),

  http.patch('/api/v1/mill-tickets/:ticketId', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('mill_tickets.create');
    if ('error' in auth) return auth.error;

    const idx = mockDb.millWeighingTickets.findIndex((t) => t.id === String(params.ticketId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const prev = mockDb.millWeighingTickets[idx];
    const body = (await request.json().catch(() => null)) as
      | components['schemas']['ReviseMillTicketRequest']
      | null;
    if (!body?.gross_weight_kg || !body?.tare_weight_kg || !body?.correction_reason) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }

    const gross = new Decimal(body.gross_weight_kg);
    const tare = new Decimal(body.tare_weight_kg);
    if (gross.isNegative() || tare.isNegative() || tare.greaterThan(gross)) {
      return makeErrorResponse('TBS_INVALID_WEIGHT');
    }

    mockDb.millWeighingTickets[idx] = { ...prev, is_current: false };
    const revised: components['schemas']['MillWeighingTicket'] = {
      ...prev,
      id: `80000000-0000-4000-8000-${Date.now().toString().slice(-12)}`,
      revision_number: prev.revision_number + 1,
      previous_ticket_id: prev.id,
      gross_weight_kg: gross.toFixed(3),
      tare_weight_kg: tare.toFixed(3),
      net_weight_kg: gross.minus(tare).toFixed(3),
      is_current: true,
      status: 'DRAFT',
      verified_at: null,
      verified_by: null,
      correction_reason: body.correction_reason,
      created_at: new Date().toISOString(),
    };
    mockDb.millWeighingTickets.unshift(revised);
    return makeSimpleEnvelope(revised);
  }),

  http.post('/api/v1/mill-tickets/:ticketId/verify', ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('mill_tickets.verify');
    if ('error' in auth) return auth.error;

    const idx = mockDb.millWeighingTickets.findIndex((t) => t.id === String(params.ticketId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.millWeighingTickets[idx];
    if (current.status === 'VERIFIED') return makeErrorResponse('MILL_TICKET_ALREADY_FINAL');

    const now = new Date().toISOString();
    const updated: components['schemas']['MillWeighingTicket'] = {
      ...current,
      status: 'VERIFIED',
      verified_at: now,
      verified_by: auth.user.id,
    };
    mockDb.millWeighingTickets[idx] = updated;

    // Update linked e-DO to RECEIVED and mark waiting reconciliation READY
    const doIdx = mockDb.deliveryOrders.findIndex((d) => d.id === current.delivery_order_id);
    if (doIdx !== -1) {
      mockDb.deliveryOrders[doIdx] = { ...mockDb.deliveryOrders[doIdx], status: 'RECEIVED' };
    }
    const recIdx = mockDb.reconciliationCases.findIndex(
      (r) => r.delivery_order_id === current.delivery_order_id && r.is_current,
    );
    if (recIdx !== -1 && mockDb.reconciliationCases[recIdx].status === 'WAITING_TICKET') {
      mockDb.reconciliationCases[recIdx] = {
        ...mockDb.reconciliationCases[recIdx],
        mill_ticket_id: updated.id,
        mill_weight_kg: updated.net_weight_kg,
        status: 'READY',
      };
    }

    appendMockAuditEvent({
      actor: auth.user,
      action: 'MILL_TICKET_VERIFIED',
      entityType: 'mill_weighing_tickets',
      entityId: updated.id,
      summary: `Tiket timbang PKS ${updated.ticket_number} diverifikasi (${updated.net_weight_kg} kg)`,
    });
    return makeSimpleEnvelope(updated);
  }),

  http.get('/api/v1/reconciliations', ({ request }) => {
    const auth = requireMockPermission('reconciliations.read');
    if ('error' in auth) return auth.error;
    const url = new URL(request.url);
    const status = (url.searchParams.get('status') ?? '').trim();
    let items = mockDb.reconciliationCases;
    if (status) {
      items = items.filter((r) => r.status === status);
    }
    return makePaginatedEnvelope(items, url);
  }),

  http.post('/api/v1/reconciliations', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('reconciliations.calculate');
    if ('error' in auth) return auth.error;

    return withMockIdempotency(request, 'createReconciliation', async () => {
      const body = (await request.json().catch(() => null)) as
        | components['schemas']['TriggerReconciliationRequest']
        | null;
      if (!body?.delivery_order_id) throw { errorResponse: makeErrorResponse('VAL_REQUIRED_FIELD') };

      const deliveryOrder = mockDb.deliveryOrders.find((d) => d.id === body.delivery_order_id);
      if (!deliveryOrder) throw { errorResponse: makeErrorResponse('SYS_RESOURCE_NOT_FOUND') };

      const ticket = mockDb.millWeighingTickets.find(
        (t) => t.delivery_order_id === deliveryOrder.id && t.is_current && t.status === 'VERIFIED',
      );
      if (!ticket) {
        throw { errorResponse: makeErrorResponse('REC_NOT_READY') };
      }

      const rule = mockDb.systemRuleVersions[0];
      const tolPct = String(
        (rule?.rule_config as { tolerance_percent?: string } | undefined)?.tolerance_percent ??
          '1.5000',
      );
      const created: components['schemas']['ReconciliationCase'] = {
        id: `90000000-0000-4000-8000-${String(mockDb.reconciliationCases.length + 201).padStart(12, '0')}`,
        delivery_order_id: deliveryOrder.id,
        delivery_order_number: deliveryOrder.delivery_order_number,
        mill_ticket_id: ticket.id,
        revision_number: 1,
        origin_weight_kg: deliveryOrder.total_origin_weight_kg,
        mill_weight_kg: ticket.net_weight_kg,
        difference_weight_kg: '0.000',
        difference_percent: '0.0000',
        tolerance_percent: tolPct,
        rule_version_id: rule?.id ?? '90000000-0000-4000-8000-000000000001',
        tolerance_policy_classification: 'SIMULATION_ONLY',
        is_negative_difference: false,
        status: 'READY',
        is_current: true,
        calculated_at: null,
        resolved_at: null,
        dispute_reviews: [],
        farmer_allocations: [],
      };
      mockDb.reconciliationCases.unshift(created);
      return { status: 201, data: created };
    }).catch((err: { errorResponse?: Response }) => {
      if (err?.errorResponse) return err.errorResponse;
      return makeErrorResponse('SYS_INTERNAL_ERROR');
    });
  }),

  http.post('/api/v1/reconciliations/:recId/calculate', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('reconciliations.calculate');
    if ('error' in auth) return auth.error;

    return withMockIdempotency(request, `calcRec:${String(params.recId)}`, async () => {
      const idx = mockDb.reconciliationCases.findIndex((r) => r.id === String(params.recId));
      if (idx === -1) throw { errorResponse: makeErrorResponse('SYS_RESOURCE_NOT_FOUND') };
      const current = mockDb.reconciliationCases[idx];
      if (!current.mill_weight_kg) {
        throw { errorResponse: makeErrorResponse('REC_NOT_READY') };
      }

      const origin = new Decimal(current.origin_weight_kg);
      const mill = new Decimal(current.mill_weight_kg);
      const diff = origin.minus(mill);
      const diffPct = diff.div(origin).times(100);
      const isNegative = diff.isNegative();
      const tol = new Decimal(current.tolerance_percent);
      const exceeds = isNegative || diffPct.abs().greaterThan(tol);

      const nextStatus: components['schemas']['ReconciliationCase']['status'] = exceeds
        ? 'DISPUTE_HOLD'
        : 'MATCHED';
      const updated: components['schemas']['ReconciliationCase'] = {
        ...current,
        difference_weight_kg: diff.toFixed(3),
        difference_percent: diffPct.toFixed(4),
        is_negative_difference: isNegative,
        status: nextStatus,
        calculated_at: new Date().toISOString(),
      };
      mockDb.reconciliationCases[idx] = updated;
      return { status: 200, data: updated };
    }).catch((err: { errorResponse?: Response }) => {
      if (err?.errorResponse) return err.errorResponse;
      return makeErrorResponse('SYS_INTERNAL_ERROR');
    });
  }),

  http.post('/api/v1/reconciliations/:recId/review', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('reconciliations.review');
    if ('error' in auth) return auth.error;

    const idx = mockDb.reconciliationCases.findIndex((r) => r.id === String(params.recId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.reconciliationCases[idx];
    const body = (await request.json().catch(() => null)) as
      | components['schemas']['DisputeReviewRequest']
      | null;
    if (!body?.decision || !body?.reason || body.reason.trim().length < 5) {
      return makeErrorResponse('REC_DISPUTE_REASON_REQUIRED');
    }

    const rev: components['schemas']['ReconciliationCase']['dispute_reviews'][number] = {
      id: `90000000-0000-4000-8000-${Date.now().toString().slice(-12)}`,
      reviewer_id: auth.user.id,
      previous_status: current.status,
      decision: body.decision,
      reason: body.reason,
      evidence_file_id: body.evidence_file_id ?? null,
      approved_by: null,
      reviewed_at: new Date().toISOString(),
    };
    const updated: components['schemas']['ReconciliationCase'] = {
      ...current,
      status: 'UNDER_REVIEW',
      dispute_reviews: [rev, ...current.dispute_reviews],
    };
    mockDb.reconciliationCases[idx] = updated;
    return makeSimpleEnvelope(updated);
  }),

  http.post('/api/v1/reconciliations/:recId/resolve', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('reconciliations.resolve');
    if ('error' in auth) return auth.error;
    if (auth.user.non_approver_admin) return makeErrorResponse('AUTH_OPERATION_FORBIDDEN');

    const idx = mockDb.reconciliationCases.findIndex((r) => r.id === String(params.recId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.reconciliationCases[idx];
    const body = (await request.json().catch(() => null)) as
      | components['schemas']['ResolveDisputeRequest']
      | null;
    if (!body?.decision || !body?.final_outcome || !body?.reason || body.reason.trim().length < 5) {
      return makeErrorResponse('REC_DISPUTE_REASON_REQUIRED');
    }

    const updated: components['schemas']['ReconciliationCase'] = {
      ...current,
      status: body.final_outcome,
      resolved_at: new Date().toISOString(),
    };
    mockDb.reconciliationCases[idx] = updated;
    appendMockAuditEvent({
      actor: auth.user,
      action: 'DISPUTE_RESOLVED',
      entityType: 'reconciliation_cases',
      entityId: updated.id,
      summary: `Sengketa ${updated.delivery_order_number} diputuskan ${body.final_outcome}: ${body.reason}`,
    });
    return makeSimpleEnvelope(updated);
  }),

  http.post('/api/v1/reconciliations/:recId/allocations', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('allocations.compute');
    if ('error' in auth) return auth.error;

    const body = (await request.json().catch(() => null)) as
      | components['schemas']['ComputeAllocationsRequest']
      | null;
    if (!body?.mode || !body?.allocation_policy_version_id) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }
    if (body.mode === 'FINAL') {
      return makeErrorResponse('REC_ALLOCATION_POLICY_UNCONFIRMED');
    }

    const idx = mockDb.reconciliationCases.findIndex((r) => r.id === String(params.recId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.reconciliationCases[idx];
    const deliveryOrder = mockDb.deliveryOrders.find((d) => d.id === current.delivery_order_id);
    const lines = deliveryOrder?.lines ?? [];
    const payableWeight = new Decimal(current.mill_weight_kg ?? current.origin_weight_kg);
    const originWeight = new Decimal(current.origin_weight_kg);
    const unitPrice = new Decimal('2850.00');

    const allocs: components['schemas']['FarmerSettlementAllocation'][] = lines.map((ln, i) => {
      const share = new Decimal(ln.origin_weight_snapshot_kg).div(originWeight);
      const agreedKg = payableWeight.times(share);
      const gross = agreedKg.times(unitPrice);
      return {
        id: `90000000-0000-4000-8000-${String(700 + i).padStart(12, '0')}`,
        receipt_id: ln.receipt_id,
        farmer_id: ln.farmer_id,
        farmer_name: ln.farmer_name,
        allocation_basis_weight_kg: ln.origin_weight_snapshot_kg,
        agreed_weight_kg: agreedKg.toFixed(3),
        allocation_policy_version_id: body.allocation_policy_version_id,
        gross_amount: gross.toFixed(2),
        deduction_amount: '0.00',
        net_amount: gross.toFixed(2),
        status: 'SIMULATED',
        policy_classification: 'SIMULATION_ONLY',
      };
    });

    mockDb.reconciliationCases[idx] = { ...current, farmer_allocations: allocs };
    return makeSimpleEnvelope(allocs);
  }),
];
