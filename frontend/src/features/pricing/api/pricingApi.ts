import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { components } from '@/lib/api/generated';
import { apiRequest } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/queryKeys';
import type { ListEnvelope, SingleEnvelope } from '@/features/master-data/api/masterDataApi';

export type PricingMetadata = components['schemas']['PricingMetadata'];
export type InternalPriceQuote = components['schemas']['InternalPriceQuote'];
export type PublicDisbunPrice = components['schemas']['PublicDisbunPrice'];

export function usePricingMetadata() {
  return useQuery({
    queryKey: queryKeys.pricing.referenceMeta(),
    queryFn: () =>
      apiRequest<SingleEnvelope<PricingMetadata>>({
        path: '/api/v1/prices/reference-meta',
      }),
  });
}

export function useInternalPrices(filters?: { status?: string; search?: string }) {
  return useQuery({
    queryKey: queryKeys.pricing.list(filters),
    queryFn: () =>
      apiRequest<ListEnvelope<InternalPriceQuote>>({
        path: '/api/v1/prices',
        query: {
          status: filters?.status || undefined,
          search: filters?.search?.trim() || undefined,
          page_size: 50,
        },
      }),
  });
}

export function useCreatePriceDraft() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: components['schemas']['CreatePriceDraftRequest']) =>
      apiRequest<SingleEnvelope<InternalPriceQuote>>({
        path: '/api/v1/prices',
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.pricing.all });
    },
  });
}

export function useSubmitPrice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (priceQuoteId: string) =>
      apiRequest<SingleEnvelope<InternalPriceQuote>>({
        path: `/api/v1/prices/${encodeURIComponent(priceQuoteId)}/submit`,
        method: 'POST',
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.pricing.all });
    },
  });
}

export function useVerifyOrRejectPrice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      priceQuoteId,
      payload,
    }: {
      priceQuoteId: string;
      payload: components['schemas']['VerifyPriceRequest'];
    }) =>
      apiRequest<SingleEnvelope<InternalPriceQuote>>({
        path: `/api/v1/prices/${encodeURIComponent(priceQuoteId)}/verify`,
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.pricing.all });
    },
  });
}

export function usePublishPrice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (priceQuoteId: string) =>
      apiRequest<SingleEnvelope<InternalPriceQuote>>({
        path: `/api/v1/prices/${encodeURIComponent(priceQuoteId)}/publish`,
        method: 'POST',
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.pricing.all });
      void qc.invalidateQueries({ queryKey: queryKeys.public.all });
    },
  });
}

export function useRevokePrice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ priceQuoteId, reason }: { priceQuoteId: string; reason: string }) =>
      apiRequest<SingleEnvelope<InternalPriceQuote>>({
        path: `/api/v1/prices/${encodeURIComponent(priceQuoteId)}/revoke`,
        method: 'POST',
        body: { reason },
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.pricing.all });
      void qc.invalidateQueries({ queryKey: queryKeys.public.all });
    },
  });
}

export function useCreateDisbunPrice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: components['schemas']['CreateDisbunPriceRequest']) =>
      apiRequest<SingleEnvelope<PublicDisbunPrice>>({
        path: '/api/v1/prices/disbun',
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.public.disbunPrices() });
    },
  });
}
