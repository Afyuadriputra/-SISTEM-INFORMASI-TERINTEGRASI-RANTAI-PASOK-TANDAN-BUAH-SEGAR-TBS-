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

export const financeHandlers = [
  http.get('/api/v1/invoices', ({ request }) => {
    const auth = requireMockPermission('invoices.read');
    if ('error' in auth) return auth.error;
    return makePaginatedEnvelope(mockDb.invoices, new URL(request.url));
  }),

  http.post('/api/v1/invoices', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('invoices.create');
    if ('error' in auth) return auth.error;

    const body = (await request.json().catch(() => null)) as
      | components['schemas']['CreateInvoiceDraftRequest']
      | null;
    if (!body?.invoice_type || !body?.creditor_party_id || !body?.debtor_party_id || !body?.reconciliation_case_id || !body?.invoice_date) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }

    const rec = mockDb.reconciliationCases.find((r) => r.id === body.reconciliation_case_id);
    if (!rec) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');

    if (rec.status !== 'MATCHED' && rec.status !== 'RESOLVED') {
      return makeErrorResponse('FIN_DISPUTE_HOLD_BLOCKED');
    }

    const deliveryOrder = mockDb.deliveryOrders.find((d) => d.id === rec.delivery_order_id);
    const contract = mockDb.tradeContracts.find((c) => c.id === deliveryOrder?.contract_id);
    const classification: components['schemas']['Invoice']['policy_classification'] =
      contract?.business_model_code === 'UNCONFIRMED' ? 'PENDING_SOP' : 'SIMULATION_ONLY';

    const weight = new Decimal(rec.mill_weight_kg ?? rec.origin_weight_kg);
    const unitPrice = new Decimal(contract?.agreed_price_per_kg ?? '2850.00');
    const gross = weight.times(unitPrice).toFixed(2);
    const invNum = `INV-${body.invoice_type === 'ACCOUNTS_RECEIVABLE' ? 'AR' : 'AP'}-2026-${String(mockDb.invoices.length + 101).padStart(3, '0')}`;

    const created: components['schemas']['Invoice'] = {
      id: `a0000000-0000-4000-8000-${String(mockDb.invoices.length + 101).padStart(12, '0')}`,
      invoice_number: invNum,
      invoice_type: body.invoice_type,
      creditor_party_id: body.creditor_party_id,
      debtor_party_id: body.debtor_party_id,
      business_model_code: contract?.business_model_code ?? 'PRINCIPAL',
      business_model_rule_version_id: rec.rule_version_id,
      reconciliation_case_id: rec.id,
      invoice_date: body.invoice_date,
      due_date: body.due_date ?? null,
      gross_amount: gross,
      deduction_amount: '0.00',
      total_amount: gross,
      status: 'DRAFT',
      settlement_status: 'UNPAID',
      policy_classification: classification,
      issued_at: null,
      verified_by: null,
      lines: [
        {
          id: `a0000000-0000-4000-8000-${Date.now().toString().slice(-12)}`,
          reference_type: 'RECONCILIATION_CASE',
          reference_id: rec.id,
          description: `Pengiriman ${rec.delivery_order_number}`,
          quantity: weight.toFixed(3),
          unit: 'kg',
          unit_price: unitPrice.toFixed(2),
          line_amount: gross,
        },
      ],
      approvals: [],
      payments: [],
      created_at: new Date().toISOString(),
    };
    mockDb.invoices.unshift(created);
    return makeSimpleEnvelope(created, undefined, 201);
  }),

  http.get('/api/v1/invoices/:invoiceId', ({ params }) => {
    const auth = requireMockPermission('invoices.read');
    if ('error' in auth) return auth.error;
    const item = mockDb.invoices.find((i) => i.id === String(params.invoiceId));
    if (!item) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    return makeSimpleEnvelope(item);
  }),

  http.post('/api/v1/invoices/:invoiceId/verify', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('invoices.verify');
    if ('error' in auth) return auth.error;
    if (auth.user.non_approver_admin) return makeErrorResponse('AUTH_OPERATION_FORBIDDEN');

    const idx = mockDb.invoices.findIndex((i) => i.id === String(params.invoiceId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.invoices[idx];
    const body = (await request.json().catch(() => null)) as
      | components['schemas']['VerifyInvoiceRequest']
      | null;
    if (!body?.decision) return makeErrorResponse('VAL_REQUIRED_FIELD');
    if (!['DRAFT', 'PENDING_VERIFICATION'].includes(current.status)) {
      return makeErrorResponse('FIN_INVOICE_NOT_VERIFIED');
    }

    const updated: components['schemas']['Invoice'] = {
      ...current,
      status: body.decision === 'APPROVE' ? 'VERIFIED' : 'REJECTED',
      verified_by: auth.user.id,
    };
    mockDb.invoices[idx] = updated;
    return makeSimpleEnvelope(updated);
  }),

  http.post('/api/v1/invoices/:invoiceId/issue', ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('invoices.issue');
    if ('error' in auth) return auth.error;

    const idx = mockDb.invoices.findIndex((i) => i.id === String(params.invoiceId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.invoices[idx];

    if (current.policy_classification === 'PENDING_SOP' || current.business_model_code === 'UNCONFIRMED') {
      return makeErrorResponse('FIN_POLICY_UNCONFIRMED');
    }
    if (current.status !== 'VERIFIED') {
      return makeErrorResponse('FIN_INVOICE_NOT_VERIFIED');
    }

    const updated: components['schemas']['Invoice'] = {
      ...current,
      status: 'ISSUED',
      settlement_status: 'AWAITING_PAYMENT',
      issued_at: new Date().toISOString(),
    };
    mockDb.invoices[idx] = updated;
    return makeSimpleEnvelope(updated);
  }),

  http.get('/api/v1/payments', ({ request }) => {
    const auth = requireMockPermission('payments.read');
    if ('error' in auth) return auth.error;
    const allPayments = mockDb.invoices.flatMap((inv) => inv.payments);
    return makePaginatedEnvelope(allPayments, new URL(request.url));
  }),

  http.post('/api/v1/payments/:invoiceId/approve', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('payments.approve');
    if ('error' in auth) {
      if (getSafeRoleNonApprover()) return makeErrorResponse('AUTH_OPERATION_FORBIDDEN');
      return auth.error;
    }
    if (auth.user.non_approver_admin) return makeErrorResponse('AUTH_OPERATION_FORBIDDEN');

    function getSafeRoleNonApprover() {
      const current = mockDb.users.find((u) => u.id === mockDb.currentUserId);
      return Boolean(current?.non_approver_admin);
    }

    return withMockIdempotency(request, `approvePayment:${String(params.invoiceId)}`, async () => {
      const idx = mockDb.invoices.findIndex((i) => i.id === String(params.invoiceId));
      if (idx === -1) throw { errorResponse: makeErrorResponse('SYS_RESOURCE_NOT_FOUND') };
      const current = mockDb.invoices[idx];

      if (current.verified_by === auth.user.id) {
        throw { errorResponse: makeErrorResponse('AUTH_CONFLICT_OF_DUTIES') };
      }

      const body = (await request.json().catch(() => null)) as
        | components['schemas']['ApprovePaymentRequest']
        | null;
      if (!body?.decision || !body?.reason || body.reason.trim().length < 5) {
        throw { errorResponse: makeErrorResponse('VAL_REQUIRED_FIELD') };
      }

      const now = new Date().toISOString();
      const approval: components['schemas']['PaymentApproval'] = {
        id: `a0000000-0000-4000-8000-${Date.now().toString().slice(-12)}`,
        requested_by: current.verified_by ?? auth.user.id,
        approver_id: auth.user.id,
        decision: body.decision,
        decision_reason: body.reason,
        requested_at: now,
        decided_at: now,
      };
      const updated: components['schemas']['Invoice'] = {
        ...current,
        approvals: [approval, ...current.approvals],
        settlement_status:
          body.decision === 'APPROVED' ? 'AWAITING_PAYMENT' : current.settlement_status,
      };
      mockDb.invoices[idx] = updated;
      appendMockAuditEvent({
        actor: auth.user,
        action: `PAYMENT_${body.decision}`,
        entityType: 'invoices',
        entityId: updated.id,
        summary: `Persetujuan pembayaran ${updated.invoice_number}: ${body.decision}`,
      });
      return { status: 200, data: updated };
    }).catch((err: { errorResponse?: Response }) => {
      if (err?.errorResponse) return err.errorResponse;
      return makeErrorResponse('SYS_INTERNAL_ERROR');
    });
  }),

  http.post('/api/v1/payments', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('payments.record');
    if ('error' in auth) return auth.error;

    return withMockIdempotency(request, 'recordPayment', async () => {
      const body = (await request.json().catch(() => null)) as
        | components['schemas']['RecordPaymentRequest']
        | null;
      if (!body?.invoice_id || !body?.amount || !body?.payment_reference || !body?.proof_file_id) {
        throw { errorResponse: makeErrorResponse('VAL_REQUIRED_FIELD') };
      }
      const idx = mockDb.invoices.findIndex((i) => i.id === body.invoice_id);
      if (idx === -1) throw { errorResponse: makeErrorResponse('SYS_RESOURCE_NOT_FOUND') };
      const invoice = mockDb.invoices[idx];

      if (invoice.status !== 'ISSUED') {
        throw { errorResponse: makeErrorResponse('FIN_INVOICE_NOT_VERIFIED') };
      }
      if (
        invoice.invoice_type === 'ACCOUNTS_PAYABLE' &&
        !invoice.approvals.some((a) => a.decision === 'APPROVED')
      ) {
        throw { errorResponse: makeErrorResponse('PAY_APPROVAL_REQUIRED') };
      }
      if (invoice.settlement_status === 'PAID') {
        throw { errorResponse: makeErrorResponse('PAY_DUPLICATE_PAYMENT') };
      }

      const paidAmt = new Decimal(body.amount);
      const totalAmt = new Decimal(invoice.total_amount);
      if (paidAmt.greaterThan(totalAmt) || paidAmt.lessThanOrEqualTo(0)) {
        throw { errorResponse: makeErrorResponse('PAY_AMOUNT_EXCEEDS_INVOICE') };
      }
      if (!paidAmt.equals(totalAmt)) {
        throw { errorResponse: makeErrorResponse('PAY_PARTIAL_NOT_SUPPORTED') };
      }

      const payRec: components['schemas']['PaymentRecord'] = {
        id: `a0000000-0000-4000-8000-${Date.now().toString().slice(-12)}`,
        payment_number: `PAY-${body.payment_direction === 'INBOUND' ? 'IN' : 'OUT'}-2026-${String(invoice.payments.length + 201).padStart(3, '0')}`,
        invoice_id: invoice.id,
        payment_direction: body.payment_direction,
        payer_party_id: body.payer_party_id,
        payee_party_id: body.payee_party_id,
        amount: paidAmt.toFixed(2),
        payment_date: body.payment_date,
        payment_method: body.payment_method,
        payment_reference: body.payment_reference.trim(),
        proof_file_id: body.proof_file_id,
        status: 'PENDING_VERIFICATION',
        recorded_by: auth.user.id,
        verified_by: null,
        verified_at: null,
        created_at: new Date().toISOString(),
      };
      invoice.payments.unshift(payRec);
      return { status: 201, data: payRec };
    }).catch((err: { errorResponse?: Response }) => {
      if (err?.errorResponse) return err.errorResponse;
      return makeErrorResponse('SYS_INTERNAL_ERROR');
    });
  }),

  http.post('/api/v1/payments/:paymentId/verify', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('payments.verify');
    if ('error' in auth) return auth.error;
    if (auth.user.non_approver_admin) return makeErrorResponse('AUTH_OPERATION_FORBIDDEN');

    const body = (await request.json().catch(() => null)) as
      | components['schemas']['VerifyPaymentRequest']
      | null;
    if (!body?.decision) return makeErrorResponse('VAL_REQUIRED_FIELD');

    for (const inv of mockDb.invoices) {
      const pIdx = inv.payments.findIndex((p) => p.id === String(params.paymentId));
      if (pIdx !== -1) {
        const pay = inv.payments[pIdx];
        if (pay.recorded_by === auth.user.id) {
          return makeErrorResponse('AUTH_CONFLICT_OF_DUTIES');
        }
        const now = new Date().toISOString();
        const updatedPay: components['schemas']['PaymentRecord'] = {
          ...pay,
          status: body.decision,
          verified_by: auth.user.id,
          verified_at: now,
        };
        inv.payments[pIdx] = updatedPay;
        if (body.decision === 'VERIFIED') {
          inv.settlement_status = 'PAID';
        }
        return makeSimpleEnvelope(updatedPay);
      }
    }
    return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
  }),
];
