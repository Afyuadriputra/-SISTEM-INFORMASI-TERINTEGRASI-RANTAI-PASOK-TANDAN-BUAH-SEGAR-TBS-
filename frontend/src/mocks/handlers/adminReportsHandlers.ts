import Decimal from 'decimal.js';
import { http } from 'msw';
import type { components } from '@/lib/api/generated';
import type { RoleCode } from '@/lib/auth/permissions';
import { mockDb } from '../mockDb';
import {
  appendMockAuditEvent,
  assertMockCsrf,
  makeErrorResponse,
  makePaginatedEnvelope,
  makeSimpleEnvelope,
  requireMockPermission,
} from '../utils';

type AdminUserSummary = components['schemas']['AdminUserSummary'];
type SystemRuleVersion = components['schemas']['SystemRuleVersion'];
type AuditEvent = components['schemas']['AuditEvent'];

const ROLE_PERMISSION_GRANTS: Record<RoleCode, string[]> = {
  FARMER: [
    'public.prices.read',
    'public.mills.read',
    'public.profile.read',
    'auth.session.read',
    'farmers.read',
    'farms.read',
    'prices.read',
    'receipts.read',
    'delivery_orders.read',
    'payments.read',
    'reports.operational.read',
  ],
  COOPERATIVE_OPERATOR: [
    'public.prices.read',
    'public.mills.read',
    'public.profile.read',
    'auth.session.read',
    'farmers.read',
    'farmers.write',
    'farms.read',
    'farms.write',
    'cooperatives.read',
    'mills.read',
    'vehicles.read',
    'vehicles.write',
    'drivers.read',
    'drivers.write',
    'prices.read',
    'receipts.read',
    'receipts.create',
    'receipts.weigh',
    'receipts.validate',
    'receipts.cancel',
    'delivery_orders.read',
    'delivery_orders.create',
    'delivery_orders.issue',
    'delivery_orders.transition',
    'delivery_orders.cancel',
    'mill_tickets.read',
    'reconciliations.read',
    'payments.read',
    'reports.operational.read',
  ],
  PERUMDA_OPERATIONS: [
    'public.prices.read',
    'public.mills.read',
    'public.profile.read',
    'auth.session.read',
    'farmers.read',
    'farmers.write',
    'farms.read',
    'farms.write',
    'cooperatives.read',
    'mills.read',
    'mills.write',
    'vehicles.read',
    'vehicles.write',
    'drivers.read',
    'drivers.write',
    'prices.read',
    'prices.create',
    'prices.submit',
    'prices.verify',
    'prices.publish',
    'prices.revoke',
    'receipts.read',
    'contracts.read',
    'contracts.write',
    'quotas.reserve',
    'quotas.consume',
    'quotas.release',
    'delivery_orders.read',
    'delivery_orders.create',
    'delivery_orders.issue',
    'delivery_orders.transition',
    'delivery_orders.cancel',
    'mill_tickets.read',
    'reconciliations.read',
    'reconciliations.calculate',
    'reconciliations.review',
    'reconciliations.resolve',
    'allocations.compute',
    'invoices.read',
    'files.upload',
    'files.read',
    'admin.rules.read',
    'admin.rules.write',
    'reports.operational.read',
  ],
  PERUMDA_FINANCE: [
    'public.prices.read',
    'public.mills.read',
    'public.profile.read',
    'auth.session.read',
    'cooperatives.read',
    'mills.read',
    'prices.read',
    'receipts.read',
    'contracts.read',
    'delivery_orders.read',
    'mill_tickets.read',
    'reconciliations.read',
    'allocations.compute',
    'invoices.read',
    'invoices.create',
    'invoices.verify',
    'invoices.issue',
    'payments.read',
    'payments.record',
    'payments.verify',
    'files.upload',
    'files.read',
    'reports.operational.read',
    'reports.finance.read',
  ],
  MILL_OPERATOR: [
    'public.prices.read',
    'public.mills.read',
    'public.profile.read',
    'auth.session.read',
    'mills.read',
    'vehicles.read',
    'delivery_orders.read',
    'delivery_orders.verify_arrival',
    'mill_tickets.read',
    'mill_tickets.create',
    'mill_tickets.verify',
    'files.upload',
    'files.read',
    'reports.operational.read',
  ],
  DIRECTOR: [
    'public.prices.read',
    'public.mills.read',
    'public.profile.read',
    'auth.session.read',
    'farmers.read',
    'farms.read',
    'cooperatives.read',
    'mills.read',
    'prices.read',
    'prices.verify',
    'receipts.read',
    'contracts.read',
    'contracts.approve',
    'delivery_orders.read',
    'mill_tickets.read',
    'reconciliations.read',
    'reconciliations.resolve',
    'invoices.read',
    'invoices.verify',
    'payments.read',
    'payments.approve',
    'files.read',
    'admin.rules.read',
    'admin.rules.write',
    'admin.audit.read',
    'reports.operational.read',
    'reports.finance.read',
  ],
  SYSTEM_ADMIN: [
    'auth.session.read',
    'admin.users.read',
    'admin.users.write',
    'admin.rules.read',
    'admin.rules.write',
    'admin.audit.read',
    'admin.health.read',
  ],
};

function defaultPeriod(url: URL) {
  const today = new Date().toISOString().slice(0, 10);
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10);
  return {
    periodFrom: url.searchParams.get('date_from') || thirtyDaysAgo,
    periodTo: url.searchParams.get('date_to') || today,
  };
}

function toAdminUserSummary(user: components['schemas']['AuthenticatedUser']): AdminUserSummary {
  return {
    id: user.id,
    username: user.username,
    email: user.email ?? null,
    status: user.status,
    failed_login_count: 0,
    last_login_at: user.last_login_at,
    roles: user.roles,
    access_scopes: user.access_scopes,
    non_approver_enforced: user.non_approver_admin || user.roles.includes('SYSTEM_ADMIN'),
  };
}

function validateScopeTarget(input: {
  scope_type: components['schemas']['ScopeType'];
  farmer_id?: string | null;
  cooperative_id?: string | null;
  mill_id?: string | null;
}): boolean {
  if (input.scope_type === 'FARMER') return Boolean(input.farmer_id);
  if (input.scope_type === 'COOPERATIVE') return Boolean(input.cooperative_id);
  if (input.scope_type === 'MILL') return Boolean(input.mill_id);
  return true;
}

export const adminReportsHandlers = [
  http.get('/health/live', () => {
    return makeSimpleEnvelope({
      status: 'ok' as const,
      service: 'agroniaga-api-mock',
      checked_at: new Date().toISOString(),
      dependencies: null,
    });
  }),

  http.get('/health/ready', () => {
    return makeSimpleEnvelope({
      status: 'ok' as const,
      service: 'agroniaga-api-mock',
      checked_at: new Date().toISOString(),
      dependencies: {
        postgresql: 'up' as const,
        redis: 'up' as const,
      },
    });
  }),

  http.get('/api/v1/reports/overview', ({ request }) => {
    const auth = requireMockPermission('reports.operational.read');
    if ('error' in auth) return auth.error;

    const { periodFrom, periodTo } = defaultPeriod(new URL(request.url));
    const roleCode = auth.user.roles[0] ?? 'PERUMDA_OPERATIONS';

    let receipts = mockDb.tbsReceipts;
    if (roleCode === 'FARMER') {
      const farmerScopeIds = auth.user.access_scopes.map((s) => s.farmer_id).filter(Boolean);
      receipts = receipts.filter((r) => farmerScopeIds.includes(r.farmer_id));
    }

    const totalWeight = receipts
      .reduce(
        (acc, r) =>
          acc.plus(new Decimal(r.net_weight_after_grading_kg ?? r.current_weighing?.net_weight_kg ?? '0')),
        new Decimal(0),
      )
      .toFixed(2);

    const activeDeliveries = mockDb.deliveryOrders.filter(
      (d) => d.status !== 'CANCELLED' && d.status !== 'COMPLETED',
    ).length;

    const matchedCount = mockDb.reconciliationCases.filter(
      (r) => r.status === 'MATCHED' || r.status === 'RESOLVED',
    ).length;
    const disputeCount = mockDb.reconciliationCases.filter(
      (r) => r.status === 'DISPUTE_HOLD',
    ).length;

    const farmerPartyIds = new Set(
      mockDb.parties.filter((pt) => pt.party_type === 'FARMER').map((pt) => pt.id),
    );
    const allPayments = mockDb.invoices.flatMap((inv) => inv.payments);
    const farmerPaid = allPayments
      .filter((p) => farmerPartyIds.has(p.payee_party_id) && p.status === 'VERIFIED')
      .reduce((acc, p) => acc.plus(new Decimal(p.amount)), new Decimal(0))
      .toFixed(2);
    const farmerPending = allPayments
      .filter((p) => farmerPartyIds.has(p.payee_party_id) && p.status === 'PENDING_VERIFICATION')
      .reduce((acc, p) => acc.plus(new Decimal(p.amount)), new Decimal(0))
      .toFixed(2);

    const payload: components['schemas']['OverviewReport'] = {
      role_code: roleCode,
      period_from: periodFrom,
      period_to: periodTo,
      total_receipts_count: receipts.length,
      total_received_weight_kg: totalWeight,
      active_deliveries_count: activeDeliveries,
      matched_reconciliations_count: matchedCount,
      dispute_reconciliations_count: disputeCount,
      farmer_paid_amount: farmerPaid,
      farmer_pending_amount: farmerPending,
      is_simulation_data: true,
      data_freshness_at: new Date().toISOString(),
    };
    return makeSimpleEnvelope(payload);
  }),

  http.get('/api/v1/reports/supply', ({ request }) => {
    const auth = requireMockPermission('reports.operational.read');
    if ('error' in auth) return auth.error;

    const url = new URL(request.url);
    const { periodFrom, periodTo } = defaultPeriod(url);
    const millFilter = url.searchParams.get('mill_id');

    const excludedCancelledCount = mockDb.deliveryOrders.filter(
      (d) => d.status === 'CANCELLED',
    ).length;

    const activeOrders = mockDb.deliveryOrders.filter(
      (d) => d.status !== 'CANCELLED' && (!millFilter || d.mill_id === millFilter),
    );

    const totalOrigin = activeOrders
      .reduce((acc, d) => acc.plus(new Decimal(d.total_origin_weight_kg ?? '0')), new Decimal(0))
      .toFixed(2);

    const byMillMap = new Map<
      string,
      { mill_id: string; mill_name: string; delivery_count: number; total_mill_weight_kg: Decimal }
    >();

    let totalMillWeight = new Decimal(0);
    for (const order of activeOrders) {
      const rec = mockDb.reconciliationCases.find((r) => r.delivery_order_id === order.id);
      const ticket = mockDb.millWeighingTickets.find((t) => t.delivery_order_id === order.id);
      const millKg = new Decimal(
        rec?.mill_weight_kg ?? ticket?.net_weight_kg ?? order.total_origin_weight_kg ?? '0',
      );
      totalMillWeight = totalMillWeight.plus(millKg);

      const mill = mockDb.mills.find((m) => m.id === order.mill_id);
      const existing = byMillMap.get(order.mill_id) ?? {
        mill_id: order.mill_id,
        mill_name: mill?.mill_name ?? order.mill_name ?? order.mill_id,
        delivery_count: 0,
        total_mill_weight_kg: new Decimal(0),
      };
      existing.delivery_count += 1;
      existing.total_mill_weight_kg = existing.total_mill_weight_kg.plus(millKg);
      byMillMap.set(order.mill_id, existing);
    }

    const payload: components['schemas']['SupplyReport'] = {
      period_from: periodFrom,
      period_to: periodTo,
      total_origin_kg: totalOrigin,
      total_mill_received_kg: totalMillWeight.toFixed(2),
      excluded_cancelled_count: excludedCancelledCount,
      by_mill: Array.from(byMillMap.values()).map((row) => ({
        mill_id: row.mill_id,
        mill_name: row.mill_name,
        delivery_count: row.delivery_count,
        total_mill_weight_kg: row.total_mill_weight_kg.toFixed(2),
      })),
      data_freshness_at: new Date().toISOString(),
    };
    return makeSimpleEnvelope(payload);
  }),

  http.get('/api/v1/reports/reconciliation', ({ request }) => {
    const auth = requireMockPermission('reports.operational.read');
    if ('error' in auth) return auth.error;

    const { periodFrom, periodTo } = defaultPeriod(new URL(request.url));
    const cases = mockDb.reconciliationCases;
    const latestRule =
      mockDb.systemRuleVersions.find((r) => r.rule_code === 'RECONCILIATION_WEIGHT_TOLERANCE') ??
      mockDb.systemRuleVersions[0];

    const payload: components['schemas']['ReconciliationReport'] = {
      period_from: periodFrom,
      period_to: periodTo,
      waiting_ticket_count: cases.filter((c) => c.status === 'WAITING_TICKET').length,
      ready_count: cases.filter((c) => c.status === 'READY').length,
      matched_count: cases.filter((c) => c.status === 'MATCHED').length,
      dispute_hold_count: cases.filter((c) => c.status === 'DISPUTE_HOLD').length,
      resolved_count: cases.filter((c) => c.status === 'RESOLVED').length,
      negative_difference_count: cases.filter((c) => c.is_negative_difference).length,
      active_rule_version_id: latestRule?.id ?? '00000000-0000-4000-8000-000000000001',
      data_freshness_at: new Date().toISOString(),
    };
    return makeSimpleEnvelope(payload);
  }),

  http.get('/api/v1/reports/finance', ({ request }) => {
    const auth = requireMockPermission('reports.finance.read');
    if ('error' in auth) return auth.error;

    const { periodFrom, periodTo } = defaultPeriod(new URL(request.url));

    const arBilled = mockDb.invoices
      .filter((i) => i.invoice_type === 'ACCOUNTS_RECEIVABLE')
      .reduce((acc, i) => acc.plus(new Decimal(i.total_amount)), new Decimal(0));

    const arCollected = mockDb.invoices
      .filter((i) => i.invoice_type === 'ACCOUNTS_RECEIVABLE' && i.settlement_status === 'PAID')
      .reduce((acc, i) => acc.plus(new Decimal(i.total_amount)), new Decimal(0));

    const apApprovedUnpaid = mockDb.invoices
      .filter(
        (i) =>
          i.invoice_type === 'ACCOUNTS_PAYABLE' &&
          (i.settlement_status === 'APPROVED_UNPAID' ||
            i.settlement_status === 'AWAITING_PAYMENT'),
      )
      .reduce((acc, i) => acc.plus(new Decimal(i.total_amount)), new Decimal(0));

    const apPaid = mockDb.invoices
      .filter((i) => i.invoice_type === 'ACCOUNTS_PAYABLE' && i.settlement_status === 'PAID')
      .reduce((acc, i) => acc.plus(new Decimal(i.total_amount)), new Decimal(0));

    const farmerPartyIds = new Set(
      mockDb.parties.filter((pt) => pt.party_type === 'FARMER').map((pt) => pt.id),
    );
    const farmerDisbursed = mockDb.invoices
      .flatMap((i) => i.payments)
      .filter((p) => farmerPartyIds.has(p.payee_party_id) && p.status === 'VERIFIED')
      .reduce((acc, p) => acc.plus(new Decimal(p.amount)), new Decimal(0));

    const grossContribution = arBilled.minus(farmerDisbursed).minus(apPaid);

    const payload: components['schemas']['FinanceReport'] = {
      period_from: periodFrom,
      period_to: periodTo,
      ar_billed_total: arBilled.toFixed(2),
      ar_cash_collected_total: arCollected.toFixed(2),
      ap_approved_unpaid_total: apApprovedUnpaid.toFixed(2),
      ap_verified_paid_total: apPaid.toFixed(2),
      farmer_disbursed_verified_total: farmerDisbursed.toFixed(2),
      gross_contribution_simulation: grossContribution.toFixed(2),
      margin_label: 'Kontribusi Kotor Niaga (Data Simulasi - Bukan Laba Bersih)',
      is_net_profit: false,
      policy_classification: 'SIMULATION_ONLY',
      data_freshness_at: new Date().toISOString(),
    };
    return makeSimpleEnvelope(payload);
  }),

  http.get('/api/v1/admin/users', ({ request }) => {
    const auth = requireMockPermission('admin.users.read');
    if ('error' in auth) return auth.error;

    const url = new URL(request.url);
    const q = (url.searchParams.get('q') ?? '').trim().toLowerCase();

    let rows = mockDb.users.map(toAdminUserSummary);
    if (q) {
      rows = rows.filter(
        (u) =>
          u.username.toLowerCase().includes(q) ||
          (u.email ?? '').toLowerCase().includes(q) ||
          u.roles.some((r) => r.toLowerCase().includes(q)),
      );
    }
    return makePaginatedEnvelope(rows, url);
  }),

  http.post('/api/v1/admin/users', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('admin.users.write');
    if ('error' in auth) return auth.error;

    const body = (await request.json().catch(() => null)) as
      | components['schemas']['CreateUserRequest']
      | null;
    if (!body?.username || !body.password || !body.role_code || !body.scope_type) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }
    if (body.username.trim().length < 3 || body.password.length < 10) {
      return makeErrorResponse('VAL_INVALID_FORMAT', {
        message: 'Username minimal 3 karakter dan kata sandi minimal 10 karakter.',
      });
    }
    if (!validateScopeTarget(body)) {
      return makeErrorResponse('VAL_REQUIRED_FIELD', {
        message: 'Scope non-global wajib menyertakan ID entitas target (Petani/Koperasi/PKS).',
      });
    }
    const exists = mockDb.users.some(
      (u) => u.username.toLowerCase() === body.username.trim().toLowerCase(),
    );
    if (exists) {
      return makeErrorResponse('MD_DUPLICATE_CODE', {
        message: 'Username sudah terdaftar pada sistem.',
      });
    }

    const newUserId = `10000000-0000-4000-8000-${String(mockDb.users.length + 1).padStart(12, '0')}`;
    const created: components['schemas']['AuthenticatedUser'] = {
      id: newUserId,
      username: body.username.trim(),
      email: body.email?.trim() || null,
      display_name: body.username.trim(),
      linked_party_id: null,
      status: 'ACTIVE',
      roles: [body.role_code],
      access_scopes: [
        {
          id: `20000000-0000-4000-8000-${String(mockDb.users.length + 1).padStart(12, '0')}`,
          scope_type: body.scope_type,
          farmer_id: body.scope_type === 'FARMER' ? (body.farmer_id ?? null) : null,
          cooperative_id:
            body.scope_type === 'COOPERATIVE' ? (body.cooperative_id ?? null) : null,
          mill_id: body.scope_type === 'MILL' ? (body.mill_id ?? null) : null,
        },
      ],
      permissions: ROLE_PERMISSION_GRANTS[body.role_code] ?? [],
      last_login_at: null,
      non_approver_admin: body.role_code === 'SYSTEM_ADMIN',
    };

    mockDb.users.unshift(created);
    appendMockAuditEvent({
      actor: auth.user,
      action: 'ADMIN_USER_CREATED',
      entityType: 'user_accounts',
      entityId: created.id,
      summary: `Akun ${created.username} dibuat dengan peran ${body.role_code} (${body.scope_type})`,
    });

    return makeSimpleEnvelope(toAdminUserSummary(created), undefined, 201);
  }),

  http.patch('/api/v1/admin/users/:userId', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('admin.users.write');
    if ('error' in auth) return auth.error;

    const userId = String(params.userId);
    const idx = mockDb.users.findIndex((u) => u.id === userId);
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');

    const body = (await request.json().catch(() => null)) as
      | components['schemas']['UpdateUserAccessRequest']
      | null;
    if (!body?.reason || body.reason.trim().length < 5) {
      return makeErrorResponse('VAL_REQUIRED_FIELD', {
        message: 'Alasan audit perubahan akun wajib diisi (minimal 5 karakter).',
      });
    }

    const current = mockDb.users[idx];
    const nextRole = body.role_code ?? current.roles[0] ?? 'FARMER';
    const nextScopeType = body.scope_type ?? current.access_scopes[0]?.scope_type ?? 'PERUMDA_GLOBAL';
    const candidateScope = {
      scope_type: nextScopeType,
      farmer_id: body.farmer_id ?? current.access_scopes[0]?.farmer_id ?? null,
      cooperative_id: body.cooperative_id ?? current.access_scopes[0]?.cooperative_id ?? null,
      mill_id: body.mill_id ?? current.access_scopes[0]?.mill_id ?? null,
    };

    if (!validateScopeTarget(candidateScope)) {
      return makeErrorResponse('VAL_REQUIRED_FIELD', {
        message: 'Perubahan cakupan non-global membutuhkan ID target yang valid.',
      });
    }

    const nextStatus = body.status ?? current.status;
    const updated: components['schemas']['AuthenticatedUser'] = {
      ...current,
      status: nextStatus,
      roles: [nextRole],
      permissions: ROLE_PERMISSION_GRANTS[nextRole] ?? current.permissions,
      non_approver_admin: nextRole === 'SYSTEM_ADMIN',
      access_scopes: [
        {
          id: current.access_scopes[0]?.id ?? `scope-${current.id}`,
          scope_type: nextScopeType,
          farmer_id: nextScopeType === 'FARMER' ? candidateScope.farmer_id : null,
          cooperative_id: nextScopeType === 'COOPERATIVE' ? candidateScope.cooperative_id : null,
          mill_id: nextScopeType === 'MILL' ? candidateScope.mill_id : null,
        },
      ],
    };

    mockDb.users[idx] = updated;
    if (nextStatus !== 'ACTIVE' && mockDb.currentUserId === updated.id) {
      mockDb.currentUserId = null;
    }

    appendMockAuditEvent({
      actor: auth.user,
      action:
        nextStatus !== current.status && nextStatus !== 'ACTIVE'
          ? 'ADMIN_USER_REVOKED'
          : 'ADMIN_USER_ACCESS_UPDATED',
      entityType: 'user_accounts',
      entityId: updated.id,
      summary: `Status=${updated.status}, peran=${nextRole}, scope=${nextScopeType}. Alasan: ${body.reason.trim()}`,
    });

    return makeSimpleEnvelope(toAdminUserSummary(updated));
  }),

  http.get('/api/v1/admin/rule-versions', ({ request }) => {
    const auth = requireMockPermission('admin.rules.read');
    if ('error' in auth) return auth.error;

    const sorted = [...mockDb.systemRuleVersions].sort((a, b) => {
      if (a.rule_code === b.rule_code) return b.version_number - a.version_number;
      return b.created_at.localeCompare(a.created_at);
    });
    return makePaginatedEnvelope(sorted, new URL(request.url));
  }),

  http.post('/api/v1/admin/rule-versions', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('admin.rules.write');
    if ('error' in auth) return auth.error;

    const body = (await request.json().catch(() => null)) as
      | components['schemas']['CreateSystemRuleVersionRequest']
      | null;
    if (!body?.rule_code || !body.effective_from || !body.policy_classification) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }

    const isSysAdmin = auth.user.roles.includes('SYSTEM_ADMIN');
    if (isSysAdmin && body.policy_classification === 'CONFIRMED') {
      return makeErrorResponse('AUTH_OPERATION_FORBIDDEN', {
        message:
          'SYSTEM_ADMIN dilarang mengesahkan kebijakan produksi (BR-SYS-002); hanya dapat mendaftarkan versi simulasi atau draf.',
      });
    }

    const maxVer = mockDb.systemRuleVersions
      .filter((r) => r.rule_code === body.rule_code)
      .reduce((max, r) => Math.max(max, r.version_number), 0);

    const approvalStatus: SystemRuleVersion['approval_status'] = isSysAdmin
      ? 'DRAFT'
      : body.policy_classification === 'CONFIRMED' && auth.user.roles.includes('DIRECTOR')
        ? 'APPROVED'
        : 'DRAFT';

    const created: SystemRuleVersion = {
      id: `90000000-0000-4000-8000-${String(mockDb.systemRuleVersions.length + 1).padStart(12, '0')}`,
      rule_code: body.rule_code.trim(),
      version_number: maxVer + 1,
      effective_from: body.effective_from,
      effective_until: body.effective_until ?? null,
      rule_config: body.rule_config,
      approval_status: approvalStatus,
      policy_classification: body.policy_classification,
      approved_by: approvalStatus === 'APPROVED' ? auth.user.id : null,
      created_at: new Date().toISOString(),
    };

    mockDb.systemRuleVersions.unshift(created);
    appendMockAuditEvent({
      actor: auth.user,
      action: 'RULE_VERSION_CREATED',
      entityType: 'system_rule_versions',
      entityId: created.id,
      summary: `Aturan baru append-only ${created.rule_code} v${created.version_number} (${created.policy_classification})`,
    });

    return makeSimpleEnvelope(created, undefined, 201);
  }),

  http.get('/api/v1/admin/audit-events', ({ request }) => {
    const auth = requireMockPermission('admin.audit.read');
    if ('error' in auth) return auth.error;

    const url = new URL(request.url);
    const modFilter = (url.searchParams.get('module') ?? '').trim().toLowerCase();
    const reqFilter = (url.searchParams.get('request_id') ?? '').trim().toLowerCase();
    const dateFrom = url.searchParams.get('date_from');
    const dateTo = url.searchParams.get('date_to');

    const mapped: AuditEvent[] = mockDb.auditEvents.map((ev) => ({
      id: ev.id,
      actor_id: ev.actor_user_id,
      event_type: ev.action,
      module: ev.entity_type,
      resource_type: ev.entity_type,
      resource_id: ev.entity_id ?? '00000000-0000-4000-8000-000000000000',
      previous_state: null,
      new_state: null,
      reason: ev.summary,
      request_id: ev.request_id,
      occurred_at: ev.created_at,
    }));

    const filtered = mapped.filter((ev) => {
      if (modFilter && !ev.module.toLowerCase().includes(modFilter)) return false;
      if (reqFilter && !ev.request_id.toLowerCase().includes(reqFilter)) return false;
      const day = ev.occurred_at.slice(0, 10);
      if (dateFrom && day < dateFrom) return false;
      if (dateTo && day > dateTo) return false;
      return true;
    });

    return makePaginatedEnvelope(filtered, url);
  }),

  http.get('/api/v1/admin/system-health', () => {
    const auth = requireMockPermission('admin.health.read');
    if ('error' in auth) return auth.error;

    const payload: components['schemas']['SystemObservabilitySummary'] = {
      health: {
        status: 'ok',
        service: 'agroniaga-api-mock',
        checked_at: new Date().toISOString(),
        dependencies: {
          postgresql: 'up',
          redis: 'up',
        },
      },
      redis_cache_hit_ratio_percent: '94.80',
      total_requests_24h: 1284,
      server_errors_5xx_24h: 1,
      recent_error_correlations: [
        {
          request_id: 'req-sim-8f2a1c90',
          trace_id: 'trc-rec-timeout-001',
          route: '/api/v1/reconciliations/calculate',
          status_code: 503,
          error_code: 'SYS_DEPENDENCY_UNAVAILABLE',
          module: 'reconciliation',
          occurred_at: '2026-11-10T04:12:00Z',
        },
      ],
    };
    return makeSimpleEnvelope(payload);
  }),
];
