import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { components } from '@/lib/api/generated';
import { apiRequest } from '@/lib/api/client';
import type { ListEnvelope, SingleEnvelope } from '@/features/master-data/api/masterDataApi';
import { queryKeys } from '@/lib/query/queryKeys';

export type MillWeighingTicket = components['schemas']['MillWeighingTicket'];
export type ReconciliationCase = components['schemas']['ReconciliationCase'];
export type FarmerSettlementAllocation = components['schemas']['FarmerSettlementAllocation'];
export type FileAsset = components['schemas']['FileAsset'];

export function useMillTickets() {
  return useQuery({
    queryKey: queryKeys.millTickets.list(),
    queryFn: () =>
      apiRequest<ListEnvelope<MillWeighingTicket>>({
        path: '/api/v1/mill-tickets',
        query: { page_size: 50 },
      }),
  });
}

export function useUploadEvidenceFile() {
  return useMutation({
    mutationFn: ({
      classification,
      file,
    }: {
      classification: 'PRICE_EVIDENCE' | 'MILL_TICKET_PROOF' | 'DISPUTE_EVIDENCE' | 'PAYMENT_PROOF';
      file: File;
    }) => {
      const formData = new FormData();
      formData.append('classification', classification);
      formData.append('file', file);
      return apiRequest<SingleEnvelope<FileAsset>>({
        path: '/api/v1/files',
        method: 'POST',
        body: formData,
      });
    },
  });
}

export function useCreateMillTicket() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: components['schemas']['CreateMillTicketRequest']) =>
      apiRequest<SingleEnvelope<MillWeighingTicket>>({
        path: '/api/v1/mill-tickets',
        method: 'POST',
        body: payload,
        idempotencyScope: `ticket:create:${payload.delivery_order_id}:${payload.ticket_number}`,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.millTickets.all });
      void qc.invalidateQueries({ queryKey: queryKeys.deliveryOrders.all });
    },
  });
}

export function useVerifyMillTicket() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (ticketId: string) =>
      apiRequest<SingleEnvelope<MillWeighingTicket>>({
        path: `/api/v1/mill-tickets/${encodeURIComponent(ticketId)}/verify`,
        method: 'POST',
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.millTickets.all });
      void qc.invalidateQueries({ queryKey: queryKeys.reconciliations.all });
      void qc.invalidateQueries({ queryKey: queryKeys.deliveryOrders.all });
    },
  });
}

export function useReconciliations(status?: string, enabled = true) {
  return useQuery({
    queryKey: queryKeys.reconciliations.list({ status }),
    queryFn: () =>
      apiRequest<ListEnvelope<ReconciliationCase>>({
        path: '/api/v1/reconciliations',
        query: { status: status || undefined, page_size: 50 },
      }),
    enabled,
  });
}

export function useTriggerReconciliation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: components['schemas']['TriggerReconciliationRequest']) =>
      apiRequest<SingleEnvelope<ReconciliationCase>>({
        path: '/api/v1/reconciliations',
        method: 'POST',
        body: payload,
        idempotencyScope: `rec:create:${payload.delivery_order_id}`,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.reconciliations.all });
    },
  });
}

export function useCalculateReconciliation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (reconciliationId: string) =>
      apiRequest<SingleEnvelope<ReconciliationCase>>({
        path: `/api/v1/reconciliations/${encodeURIComponent(reconciliationId)}/calculate`,
        method: 'POST',
        idempotencyScope: `rec:calc:${reconciliationId}`,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.reconciliations.all });
    },
  });
}

export function useSubmitDisputeReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      reconciliationId,
      payload,
    }: {
      reconciliationId: string;
      payload: components['schemas']['DisputeReviewRequest'];
    }) =>
      apiRequest<SingleEnvelope<ReconciliationCase>>({
        path: `/api/v1/reconciliations/${encodeURIComponent(reconciliationId)}/review`,
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.reconciliations.all });
    },
  });
}

export function useResolveDispute() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      reconciliationId,
      payload,
    }: {
      reconciliationId: string;
      payload: components['schemas']['ResolveDisputeRequest'];
    }) =>
      apiRequest<SingleEnvelope<ReconciliationCase>>({
        path: `/api/v1/reconciliations/${encodeURIComponent(reconciliationId)}/resolve`,
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.reconciliations.all });
    },
  });
}

export function useComputeAllocations() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      reconciliationId,
      payload,
    }: {
      reconciliationId: string;
      payload: components['schemas']['ComputeAllocationsRequest'];
    }) =>
      apiRequest<SingleEnvelope<FarmerSettlementAllocation[]>>({
        path: `/api/v1/reconciliations/${encodeURIComponent(reconciliationId)}/allocations`,
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.reconciliations.all });
    },
  });
}
