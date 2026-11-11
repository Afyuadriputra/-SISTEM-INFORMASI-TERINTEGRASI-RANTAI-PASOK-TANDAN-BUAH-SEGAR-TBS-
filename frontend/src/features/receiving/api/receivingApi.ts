import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { components } from '@/lib/api/generated';
import { apiRequest } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/queryKeys';
import type { ListEnvelope, SingleEnvelope } from '@/features/master-data/api/masterDataApi';

export type TbsReceipt = components['schemas']['TbsReceipt'];

export function useReceipts(filters?: { status?: string }) {
  return useQuery({
    queryKey: queryKeys.receipts.list(filters),
    queryFn: () =>
      apiRequest<ListEnvelope<TbsReceipt>>({
        path: '/api/v1/receipts',
        query: { status: filters?.status || undefined, page_size: 50 },
      }),
  });
}

export function useCreateReceiptDraft() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      payload,
      idempotencyScope,
    }: {
      payload: components['schemas']['CreateReceiptRequest'];
      idempotencyScope?: string;
    }) =>
      apiRequest<SingleEnvelope<TbsReceipt>>({
        path: '/api/v1/receipts',
        method: 'POST',
        body: payload,
        idempotencyScope: idempotencyScope ?? `receipt:create:${payload.farmer_id}:${payload.farm_id}`,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.receipts.all });
    },
  });
}

export function useRecordWeighing() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      receiptId,
      payload,
    }: {
      receiptId: string;
      payload: components['schemas']['RecordWeighingRequest'];
    }) =>
      apiRequest<SingleEnvelope<TbsReceipt>>({
        path: `/api/v1/receipts/${encodeURIComponent(receiptId)}/weighing`,
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.receipts.all });
    },
  });
}

export function useRecordGrading() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      receiptId,
      payload,
    }: {
      receiptId: string;
      payload: components['schemas']['RecordGradingRequest'];
    }) =>
      apiRequest<SingleEnvelope<TbsReceipt>>({
        path: `/api/v1/receipts/${encodeURIComponent(receiptId)}/grading`,
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.receipts.all });
    },
  });
}

export function useValidateReceipt() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ receiptId, version }: { receiptId: string; version: number }) =>
      apiRequest<SingleEnvelope<TbsReceipt>>({
        path: `/api/v1/receipts/${encodeURIComponent(receiptId)}/validate`,
        method: 'POST',
        body: { reason: 'Validasi data timbang & grading koperasi', version },
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.receipts.all });
    },
  });
}

export function useCancelReceipt() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      receiptId,
      reason,
      version,
    }: {
      receiptId: string;
      reason: string;
      version: number;
    }) =>
      apiRequest<SingleEnvelope<TbsReceipt>>({
        path: `/api/v1/receipts/${encodeURIComponent(receiptId)}/cancel`,
        method: 'POST',
        body: { reason, version },
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.receipts.all });
    },
  });
}
