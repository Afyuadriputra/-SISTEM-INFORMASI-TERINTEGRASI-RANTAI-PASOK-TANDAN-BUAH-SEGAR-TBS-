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

export const logisticsHandlers = [
  http.get('/api/v1/contracts', ({ request }) => {
    const auth = requireMockPermission('contracts.read');
    if ('error' in auth) return auth.error;
    return makePaginatedEnvelope(mockDb.tradeContracts, new URL(request.url));
  }),

  http.post('/api/v1/contracts', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('contracts.write');
    if ('error' in auth) return auth.error;

    const body = (await request.json().catch(() => null)) as
      | components['schemas']['CreateContractRequest']
      | null;
    if (!body?.contract_number || !body?.mill_id || !body?.start_date || !body?.end_date) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }
    const mill = mockDb.mills.find((m) => m.id === body.mill_id);
    if (!mill) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    if (mockDb.tradeContracts.some((c) => c.contract_number === body.contract_number)) {
      return makeErrorResponse('MD_DUPLICATE_CODE');
    }

    const quotaStr = new Decimal(body.initial_quota_kg).toFixed(3);
    const now = new Date().toISOString();
    const created: components['schemas']['TradeContract'] = {
      id: `60000000-0000-4000-8000-${String(mockDb.tradeContracts.length + 10).padStart(12, '0')}`,
      contract_number: body.contract_number.trim(),
      mill_id: mill.id,
      mill_name: mill.mill_name,
      start_date: body.start_date,
      end_date: body.end_date,
      price_rule_type: body.price_rule_type,
      agreed_price_per_kg: body.agreed_price_per_kg ?? null,
      business_model_code: body.business_model_code,
      perumda_role: body.perumda_role,
      seller_party_id: body.seller_party_id,
      buyer_party_id: body.buyer_party_id,
      agent_party_id: body.agent_party_id ?? null,
      represented_party_id: body.represented_party_id ?? null,
      business_model_rule_version: 'MODEL_V1_PENDING_SOP',
      payment_terms: body.payment_terms,
      status: 'PENDING_APPROVAL',
      policy_classification:
        body.business_model_code === 'UNCONFIRMED' ? 'PENDING_SOP' : 'SIMULATION_ONLY',
      quota_periods: [
        {
          id: `60000000-0000-4000-8000-${String(mockDb.tradeContracts.length + 901).padStart(12, '0')}`,
          period_start: body.start_date,
          period_end: body.end_date,
          quota_limit_kg: quotaStr,
          consumed_weight_kg: '0.000',
          active_reserved_kg: '0.000',
          available_quota_kg: quotaStr,
          status: 'ACTIVE',
        },
      ],
      approved_by: null,
      approved_at: null,
      created_at: now,
    };
    mockDb.tradeContracts.unshift(created);
    return makeSimpleEnvelope(created, undefined, 201);
  }),

  http.get('/api/v1/contracts/:contractId', ({ params }) => {
    const auth = requireMockPermission('contracts.read');
    if ('error' in auth) return auth.error;
    const item = mockDb.tradeContracts.find((c) => c.id === String(params.contractId));
    if (!item) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    return makeSimpleEnvelope(item);
  }),

  http.post('/api/v1/contracts/:contractId/approve', ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('contracts.approve');
    if ('error' in auth) return auth.error;
    if (auth.user.non_approver_admin) return makeErrorResponse('AUTH_OPERATION_FORBIDDEN');

    const idx = mockDb.tradeContracts.findIndex((c) => c.id === String(params.contractId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.tradeContracts[idx];
    const updated: components['schemas']['TradeContract'] = {
      ...current,
      status: 'ACTIVE',
      approved_by: auth.user.id,
      approved_at: new Date().toISOString(),
    };
    mockDb.tradeContracts[idx] = updated;
    appendMockAuditEvent({
      actor: auth.user,
      action: 'CONTRACT_APPROVED',
      entityType: 'trade_contracts',
      entityId: updated.id,
      summary: `Kontrak ${updated.contract_number} disetujui Direksi`,
    });
    return makeSimpleEnvelope(updated);
  }),

  http.get('/api/v1/contracts/:contractId/quota', ({ params }) => {
    const auth = requireMockPermission('contracts.read');
    if ('error' in auth) return auth.error;
    const contract = mockDb.tradeContracts.find((c) => c.id === String(params.contractId));
    if (!contract) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    return makeSimpleEnvelope(contract.quota_periods);
  }),

  http.post('/api/v1/contracts/:contractId/reservations', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('quotas.reserve');
    if ('error' in auth) return auth.error;

    return withMockIdempotency(request, `reserveQuota:${String(params.contractId)}`, async () => {
      const contractIdx = mockDb.tradeContracts.findIndex((c) => c.id === String(params.contractId));
      if (contractIdx === -1) throw { errorResponse: makeErrorResponse('SYS_RESOURCE_NOT_FOUND') };
      const contract = mockDb.tradeContracts[contractIdx];
      if (contract.status !== 'ACTIVE') {
        throw { errorResponse: makeErrorResponse('CONTRACT_NOT_ACTIVE') };
      }

      const body = (await request.json().catch(() => null)) as
        | components['schemas']['ReserveQuotaRequest']
        | null;
      if (!body?.quota_period_id || !body?.delivery_order_id || !body?.reserved_weight_kg) {
        throw { errorResponse: makeErrorResponse('VAL_REQUIRED_FIELD') };
      }

      const periodIdx = contract.quota_periods.findIndex((q) => q.id === body.quota_period_id);
      if (periodIdx === -1) throw { errorResponse: makeErrorResponse('SYS_RESOURCE_NOT_FOUND') };
      const period = contract.quota_periods[periodIdx];

      const requestedKg = new Decimal(body.reserved_weight_kg);
      const availKg = new Decimal(period.available_quota_kg);
      if (requestedKg.greaterThan(availKg)) {
        throw { errorResponse: makeErrorResponse('CONTRACT_QUOTA_EXCEEDED') };
      }

      const nextReserved = new Decimal(period.active_reserved_kg).plus(requestedKg).toFixed(3);
      const nextAvail = availKg.minus(requestedKg).toFixed(3);
      contract.quota_periods[periodIdx] = {
        ...period,
        active_reserved_kg: nextReserved,
        available_quota_kg: nextAvail,
      };

      const resv: components['schemas']['QuotaReservation'] = {
        id: `60000000-0000-4000-8000-${Date.now().toString().slice(-12)}`,
        quota_period_id: period.id,
        delivery_order_id: body.delivery_order_id,
        reserved_weight_kg: requestedKg.toFixed(3),
        consumed_weight_kg: '0.000',
        status: 'RESERVED',
        reserved_at: new Date().toISOString(),
      };
      mockDb.quotaReservations.unshift(resv);
      return { status: 201, data: resv };
    }).catch((err: { errorResponse?: Response }) => {
      if (err?.errorResponse) return err.errorResponse;
      return makeErrorResponse('SYS_INTERNAL_ERROR');
    });
  }),

  http.get('/api/v1/delivery-orders', ({ request }) => {
    const auth = requireMockPermission('delivery_orders.read');
    if ('error' in auth) return auth.error;

    const url = new URL(request.url);
    const status = (url.searchParams.get('status') ?? '').trim();
    const coopScope = auth.user.access_scopes.find((s) => s.scope_type === 'COOPERATIVE')?.cooperative_id;
    const millScope = auth.user.access_scopes.find((s) => s.scope_type === 'MILL')?.mill_id;

    let items = mockDb.deliveryOrders;
    if (coopScope) items = items.filter((d) => d.cooperative_id === coopScope);
    if (millScope) items = items.filter((d) => d.mill_id === millScope);
    if (status) items = items.filter((d) => d.status === status);
    return makePaginatedEnvelope(items, url);
  }),

  http.post('/api/v1/delivery-orders', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('delivery_orders.create');
    if ('error' in auth) return auth.error;

    const body = (await request.json().catch(() => null)) as
      | components['schemas']['CreateDeliveryOrderDraftRequest']
      | null;
    if (!body?.mill_id || !body?.contract_id || !body?.vehicle_id || !body?.driver_id || !body?.receipt_ids?.length) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }

    const mill = mockDb.mills.find((m) => m.id === body.mill_id);
    const contract = mockDb.tradeContracts.find((c) => c.id === body.contract_id);
    const vehicle = mockDb.vehicles.find((v) => v.id === body.vehicle_id);
    const driver = mockDb.drivers.find((d) => d.id === body.driver_id);
    if (!mill || !contract || !vehicle || !driver) {
      return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    }

    let totalWeight = new Decimal(0);
    const lines: components['schemas']['DeliveryOrderLine'][] = [];

    for (const rid of body.receipt_ids) {
      const rcp = mockDb.tbsReceipts.find((r) => r.id === rid);
      if (!rcp) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
      if (['ALLOCATED', 'SHIPPED', 'CLOSED'].includes(rcp.status)) {
        return makeErrorResponse('LOG_DELIVERY_ALREADY_ASSIGNED');
      }
      if (rcp.status !== 'VALIDATED' || !rcp.current_weighing) {
        return makeErrorResponse('TBS_INVALID_STATE_TRANSITION', {
          message: `Penerimaan ${rcp.receipt_number} belum divalidasi untuk dimuat ke e-DO.`,
        });
      }
      const w = new Decimal(rcp.current_weighing.net_weight_kg);
      totalWeight = totalWeight.plus(w);
      lines.push({
        id: `70000000-0000-4000-8000-${String(lines.length + 1).padStart(12, '0')}`,
        receipt_id: rcp.id,
        receipt_number: rcp.receipt_number,
        farmer_id: rcp.farmer_id,
        farmer_name: rcp.farmer_name,
        origin_weight_snapshot_kg: w.toFixed(3),
        allocation_status: 'ACTIVE',
      });
    }

    // Lock receipts immediately on e-DO draft creation
    for (const rid of body.receipt_ids) {
      const idx = mockDb.tbsReceipts.findIndex((r) => r.id === rid);
      if (idx !== -1) {
        mockDb.tbsReceipts[idx] = { ...mockDb.tbsReceipts[idx], status: 'ALLOCATED' };
      }
    }

    const coopScope = auth.user.access_scopes.find((s) => s.scope_type === 'COOPERATIVE')?.cooperative_id;
    const now = new Date().toISOString();
    const doNum = `EDO-2026-${String(mockDb.deliveryOrders.length + 101).padStart(4, '0')}`;
    const created: components['schemas']['DeliveryOrder'] = {
      id: `70000000-0000-4000-8000-${String(mockDb.deliveryOrders.length + 101).padStart(12, '0')}`,
      delivery_order_number: doNum,
      cooperative_id: coopScope ?? mockDb.cooperatives[0].id,
      mill_id: mill.id,
      mill_name: mill.mill_name,
      contract_id: contract.id,
      vehicle_id: vehicle.id,
      vehicle_plate: vehicle.plate_number,
      driver_id: driver.id,
      driver_name: driver.full_name,
      total_origin_weight_kg: totalWeight.toFixed(3),
      status: 'DRAFT',
      gps_tracking_supported: false,
      qr_verification_token: `QR-${doNum}`,
      lines,
      status_events: [
        {
          id: `ev-${Date.now()}`,
          previous_status: null,
          new_status: 'DRAFT',
          actor_id: auth.user.id,
          event_time: now,
          reason: 'Penyusunan muatan e-DO multi-petani',
        },
      ],
      issued_at: null,
      departed_at: null,
      arrived_at: null,
      completed_at: null,
      version: 1,
      created_at: now,
    };
    mockDb.deliveryOrders.unshift(created);
    return makeSimpleEnvelope(created, undefined, 201);
  }),

  http.get('/api/v1/delivery-orders/:deliveryOrderId', ({ params }) => {
    const auth = requireMockPermission('delivery_orders.read');
    if ('error' in auth) return auth.error;
    const item = mockDb.deliveryOrders.find((d) => d.id === String(params.deliveryOrderId));
    if (!item) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    return makeSimpleEnvelope(item);
  }),

  http.post('/api/v1/delivery-orders/:deliveryOrderId/issue', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('delivery_orders.issue');
    if ('error' in auth) return auth.error;

    return withMockIdempotency(request, `issueDo:${String(params.deliveryOrderId)}`, async () => {
      const idx = mockDb.deliveryOrders.findIndex((d) => d.id === String(params.deliveryOrderId));
      if (idx === -1) throw { errorResponse: makeErrorResponse('SYS_RESOURCE_NOT_FOUND') };
      const current = mockDb.deliveryOrders[idx];
      if (current.status !== 'DRAFT') {
        throw { errorResponse: makeErrorResponse('LOG_INVALID_STATE_TRANSITION') };
      }
      const contract = mockDb.tradeContracts.find((c) => c.id === current.contract_id);
      const period = contract?.quota_periods[0];
      if (period && new Decimal(current.total_origin_weight_kg).greaterThan(period.available_quota_kg)) {
        throw { errorResponse: makeErrorResponse('CONTRACT_QUOTA_EXCEEDED') };
      }

      const now = new Date().toISOString();
      const updated: components['schemas']['DeliveryOrder'] = {
        ...current,
        status: 'READY',
        issued_at: now,
        version: current.version + 1,
        status_events: [
          ...current.status_events,
          {
            id: `ev-${Date.now()}`,
            previous_status: 'DRAFT',
            new_status: 'READY',
            actor_id: auth.user.id,
            event_time: now,
            reason: 'Penerbitan resmi surat jalan e-DO',
          },
        ],
      };
      mockDb.deliveryOrders[idx] = updated;
      return { status: 200, data: updated };
    }).catch((err: { errorResponse?: Response }) => {
      if (err?.errorResponse) return err.errorResponse;
      return makeErrorResponse('SYS_INTERNAL_ERROR');
    });
  }),

  http.post('/api/v1/delivery-orders/:deliveryOrderId/status', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('delivery_orders.transition');
    if ('error' in auth) return auth.error;

    const idx = mockDb.deliveryOrders.findIndex((d) => d.id === String(params.deliveryOrderId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.deliveryOrders[idx];
    const body = (await request.json().catch(() => null)) as
      | components['schemas']['TransitionDeliveryStatusRequest']
      | null;
    if (!body?.target_status) return makeErrorResponse('VAL_REQUIRED_FIELD');
    if (body.version !== current.version) return makeErrorResponse('LOG_STALE_RECORD_VERSION');

    const now = new Date().toISOString();
    const updated: components['schemas']['DeliveryOrder'] = {
      ...current,
      status: body.target_status,
      departed_at: body.target_status === 'IN_TRANSIT' ? now : current.departed_at,
      arrived_at: body.target_status === 'ARRIVED' ? now : current.arrived_at,
      completed_at: body.target_status === 'COMPLETED' ? now : current.completed_at,
      version: current.version + 1,
      status_events: [
        ...current.status_events,
        {
          id: `ev-${Date.now()}`,
          previous_status: current.status,
          new_status: body.target_status,
          actor_id: auth.user.id,
          event_time: now,
          reason: body.reason ?? 'Pembaruan status pengiriman',
        },
      ],
    };
    mockDb.deliveryOrders[idx] = updated;
    return makeSimpleEnvelope(updated);
  }),

  http.post('/api/v1/delivery-orders/:deliveryOrderId/cancel', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('delivery_orders.cancel');
    if ('error' in auth) return auth.error;

    const idx = mockDb.deliveryOrders.findIndex((d) => d.id === String(params.deliveryOrderId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.deliveryOrders[idx];
    if (['ARRIVED', 'RECEIVED', 'COMPLETED'].includes(current.status)) {
      return makeErrorResponse('LOG_CANCELLATION_FORBIDDEN');
    }
    const body = (await request.json().catch(() => null)) as { reason?: string; version?: number } | null;
    if (!body?.reason || body.reason.trim().length < 3) return makeErrorResponse('VAL_REQUIRED_FIELD');

    for (const ln of current.lines) {
      const rIdx = mockDb.tbsReceipts.findIndex((r) => r.id === ln.receipt_id);
      if (rIdx !== -1 && mockDb.tbsReceipts[rIdx].status === 'ALLOCATED') {
        mockDb.tbsReceipts[rIdx] = { ...mockDb.tbsReceipts[rIdx], status: 'VALIDATED' };
      }
    }

    const updated: components['schemas']['DeliveryOrder'] = {
      ...current,
      status: 'CANCELLED',
      version: current.version + 1,
    };
    mockDb.deliveryOrders[idx] = updated;
    return makeSimpleEnvelope(updated);
  }),

  http.post('/api/v1/delivery-orders/verify-qr', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('delivery_orders.verify_arrival');
    if ('error' in auth) return auth.error;

    const body = (await request.json().catch(() => null)) as
      | components['schemas']['VerifyDeliveryQrRequest']
      | null;
    if (!body?.qr_token_or_edo_number) return makeErrorResponse('VAL_REQUIRED_FIELD');

    const needle = body.qr_token_or_edo_number.trim();
    const idx = mockDb.deliveryOrders.findIndex(
      (d) => d.qr_verification_token === needle || d.delivery_order_number === needle,
    );
    if (idx === -1) return makeErrorResponse('LOG_QR_VERIFICATION_FAILED');

    const current = mockDb.deliveryOrders[idx];
    const millScope = auth.user.access_scopes.find((s) => s.scope_type === 'MILL')?.mill_id;
    if (millScope && current.mill_id !== millScope) {
      return makeErrorResponse('MILL_EDO_MILL_MISMATCH');
    }

    const now = new Date().toISOString();
    const nextStatus = current.status === 'IN_TRANSIT' || current.status === 'READY' ? 'ARRIVED' : current.status;
    const updated: components['schemas']['DeliveryOrder'] = {
      ...current,
      status: nextStatus,
      arrived_at: current.arrived_at ?? now,
      status_events: [
        ...current.status_events,
        {
          id: `ev-${Date.now()}`,
          previous_status: current.status,
          new_status: nextStatus,
          actor_id: auth.user.id,
          event_time: now,
          reason: `Verifikasi kedatangan e-DO di PKS (${body.observed_plate_number ?? current.vehicle_plate})`,
        },
      ],
    };
    mockDb.deliveryOrders[idx] = updated;
    return makeSimpleEnvelope(updated);
  }),
];
