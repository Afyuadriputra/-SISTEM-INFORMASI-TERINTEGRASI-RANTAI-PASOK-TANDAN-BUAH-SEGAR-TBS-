import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { components } from '@/lib/api/generated';
import { apiRequest } from '@/lib/api/client';
import type { ListEnvelope, SingleEnvelope } from '@/features/master-data/api/masterDataApi';
import { queryKeys } from '@/lib/query/queryKeys';

export type TradeContract = components['schemas']['TradeContract'];
export type QuotaReservation = components['schemas']['QuotaReservation'];
export type DeliveryOrder = components['schemas']['DeliveryOrder'];

export function useContracts(enabled = true) {
  return useQuery({
    queryKey: queryKeys.contracts.list(),
    queryFn: () =>
      apiRequest<ListEnvelope<TradeContract>>({
        path: '/api/v1/contracts',
        query: { page_size: 50 },
      }),
    enabled,
  });
}

export function useCreateContract() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: components['schemas']['CreateContractRequest']) =>
      apiRequest<SingleEnvelope<TradeContract>>({
        path: '/api/v1/contracts',
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.contracts.all });
    },
  });
}

export function useApproveContract() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (contractId: string) =>
      apiRequest<SingleEnvelope<TradeContract>>({
        path: `/api/v1/contracts/${encodeURIComponent(contractId)}/approve`,
        method: 'POST',
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.contracts.all });
    },
  });
}

export function useReserveQuota() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      contractId,
      payload,
    }: {
      contractId: string;
      payload: components['schemas']['ReserveQuotaRequest'];
    }) =>
      apiRequest<SingleEnvelope<QuotaReservation>>({
        path: `/api/v1/contracts/${encodeURIComponent(contractId)}/reservations`,
        method: 'POST',
        body: payload,
        idempotencyScope: `quota:reserve:${contractId}:${payload.delivery_order_id}`,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.contracts.all });
    },
  });
}

export function useDeliveryOrders(filters?: { status?: string }, enabled = true) {
  return useQuery({
    queryKey: queryKeys.deliveryOrders.list(filters),
    queryFn: () =>
      apiRequest<ListEnvelope<DeliveryOrder>>({
        path: '/api/v1/delivery-orders',
        query: { status: filters?.status || undefined, page_size: 50 },
      }),
    enabled,
  });
}

export function useCreateDeliveryOrderDraft() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: components['schemas']['CreateDeliveryOrderDraftRequest']) =>
      apiRequest<SingleEnvelope<DeliveryOrder>>({
        path: '/api/v1/delivery-orders',
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.deliveryOrders.all });
      void qc.invalidateQueries({ queryKey: queryKeys.receipts.all });
    },
  });
}

export function useIssueDeliveryOrder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ deliveryOrderId, version }: { deliveryOrderId: string; version: number }) =>
      apiRequest<SingleEnvelope<DeliveryOrder>>({
        path: `/api/v1/delivery-orders/${encodeURIComponent(deliveryOrderId)}/issue`,
        method: 'POST',
        body: { version, confirm_lock_allocations: true },
        idempotencyScope: `edo:issue:${deliveryOrderId}`,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.deliveryOrders.all });
      void qc.invalidateQueries({ queryKey: queryKeys.contracts.all });
      void qc.invalidateQueries({ queryKey: queryKeys.receipts.all });
    },
  });
}

export function useTransitionDeliveryStatus() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      deliveryOrderId,
      payload,
    }: {
      deliveryOrderId: string;
      payload: components['schemas']['TransitionDeliveryStatusRequest'];
    }) =>
      apiRequest<SingleEnvelope<DeliveryOrder>>({
        path: `/api/v1/delivery-orders/${encodeURIComponent(deliveryOrderId)}/status`,
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.deliveryOrders.all });
    },
  });
}

export function useCancelDeliveryOrder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      deliveryOrderId,
      reason,
      version,
    }: {
      deliveryOrderId: string;
      reason: string;
      version: number;
    }) =>
      apiRequest<SingleEnvelope<DeliveryOrder>>({
        path: `/api/v1/delivery-orders/${encodeURIComponent(deliveryOrderId)}/cancel`,
        method: 'POST',
        body: { reason, version },
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.deliveryOrders.all });
      void qc.invalidateQueries({ queryKey: queryKeys.receipts.all });
    },
  });
}

export function useVerifyDeliveryQr() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: components['schemas']['VerifyDeliveryQrRequest']) =>
      apiRequest<SingleEnvelope<DeliveryOrder>>({
        path: '/api/v1/delivery-orders/verify-qr',
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.deliveryOrders.all });
    },
  });
}
