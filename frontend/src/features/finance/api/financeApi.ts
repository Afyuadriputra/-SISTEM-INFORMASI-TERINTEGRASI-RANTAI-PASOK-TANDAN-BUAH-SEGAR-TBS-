import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { components } from '@/lib/api/generated';
import { apiRequest } from '@/lib/api/client';
import type { ListEnvelope, SingleEnvelope } from '@/features/master-data/api/masterDataApi';
import { queryKeys } from '@/lib/query/queryKeys';

export type Invoice = components['schemas']['Invoice'];
export type PaymentRecord = components['schemas']['PaymentRecord'];

export function useInvoices(enabled = true) {
  return useQuery({
    queryKey: queryKeys.finance.invoices(),
    queryFn: () =>
      apiRequest<ListEnvelope<Invoice>>({
        path: '/api/v1/invoices',
        query: { page_size: 50 },
      }),
    enabled,
  });
}

export function usePayments() {
  return useQuery({
    queryKey: queryKeys.finance.payments(),
    queryFn: () =>
      apiRequest<ListEnvelope<PaymentRecord>>({
        path: '/api/v1/payments',
        query: { page_size: 50 },
      }),
  });
}

export function useCreateInvoiceDraft() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: components['schemas']['CreateInvoiceDraftRequest']) =>
      apiRequest<SingleEnvelope<Invoice>>({
        path: '/api/v1/invoices',
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.finance.all });
    },
  });
}

export function useVerifyInvoice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      invoiceId,
      payload,
    }: {
      invoiceId: string;
      payload: components['schemas']['VerifyInvoiceRequest'];
    }) =>
      apiRequest<SingleEnvelope<Invoice>>({
        path: `/api/v1/invoices/${encodeURIComponent(invoiceId)}/verify`,
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.finance.all });
    },
  });
}

export function useIssueInvoice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (invoiceId: string) =>
      apiRequest<SingleEnvelope<Invoice>>({
        path: `/api/v1/invoices/${encodeURIComponent(invoiceId)}/issue`,
        method: 'POST',
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.finance.all });
    },
  });
}

export function useApproveOrRejectPayment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      invoiceId,
      payload,
    }: {
      invoiceId: string;
      payload: components['schemas']['ApprovePaymentRequest'];
    }) =>
      apiRequest<SingleEnvelope<Invoice>>({
        path: `/api/v1/payments/${encodeURIComponent(invoiceId)}/approve`,
        method: 'POST',
        body: payload,
        idempotencyScope: `pay:approve:${invoiceId}:${payload.decision}`,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.finance.all });
    },
  });
}

export function useRecordPayment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: components['schemas']['RecordPaymentRequest']) =>
      apiRequest<SingleEnvelope<PaymentRecord>>({
        path: '/api/v1/payments',
        method: 'POST',
        body: payload,
        idempotencyScope: `pay:record:${payload.invoice_id}:${payload.payment_reference}`,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.finance.all });
    },
  });
}

export function useVerifyPayment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      paymentId,
      payload,
    }: {
      paymentId: string;
      payload: components['schemas']['VerifyPaymentRequest'];
    }) =>
      apiRequest<SingleEnvelope<PaymentRecord>>({
        path: `/api/v1/payments/${encodeURIComponent(paymentId)}/verify`,
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.finance.all });
    },
  });
}
