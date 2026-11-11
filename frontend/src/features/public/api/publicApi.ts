import { useQuery } from '@tanstack/react-query';
import type { components } from '@/lib/api/generated';
import { apiRequest } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/queryKeys';

export type PublicPriceListEnvelope = components['schemas']['PublicPriceListEnvelope'];
export type PublicPriceDetailEnvelope = components['schemas']['PublicPriceDetailEnvelope'];
export type PublicDisbunPriceListEnvelope = components['schemas']['PublicDisbunPriceListEnvelope'];
export type PublicMillListEnvelope = components['schemas']['PublicMillListEnvelope'];
export type PublicMillDetailEnvelope = components['schemas']['PublicMillDetailEnvelope'];
export type PublicProfileEnvelope = components['schemas']['PublicProfileEnvelope'];
export type PublicNoticeListEnvelope = components['schemas']['PublicNoticeListEnvelope'];

export interface PublicPriceQueryParams {
  readonly search?: string;
  readonly regency?: string;
  readonly category_code?: string;
  readonly sort_by?: 'price_per_kg' | 'mill_name' | 'updated_at';
  readonly sort_dir?: 'asc' | 'desc';
  readonly include_expired?: boolean;
  readonly page?: number;
  readonly page_size?: number;
}

export function usePublicPrices(params: PublicPriceQueryParams = {}) {
  return useQuery({
    queryKey: queryKeys.public.prices({ ...params }),
    queryFn: () =>
      apiRequest<PublicPriceListEnvelope>({
        path: '/api/v1/public/prices',
        query: {
          q: params.search,
          regency: params.regency,
          category_code: params.category_code,
          sort_by: params.sort_by,
          sort_dir: params.sort_dir,
          include_expired: params.include_expired,
          page: params.page ?? 1,
          page_size: params.page_size ?? 20,
        },
      }),
  });
}

export function usePublicDisbunPrices() {
  return useQuery({
    queryKey: queryKeys.public.disbunPrices(),
    queryFn: () =>
      apiRequest<PublicDisbunPriceListEnvelope>({
        path: '/api/v1/public/disbun-prices',
      }),
  });
}

export function usePublicMills(params: { search?: string; regency?: string; page?: number; page_size?: number } = {}) {
  return useQuery({
    queryKey: queryKeys.public.mills({ ...params }),
    queryFn: () =>
      apiRequest<PublicMillListEnvelope>({
        path: '/api/v1/public/mills',
        query: {
          q: params.search,
          regency: params.regency,
          page: params.page ?? 1,
          page_size: params.page_size ?? 20,
        },
      }),
  });
}

export function usePublicMillDetail(millId: string) {
  return useQuery({
    queryKey: queryKeys.public.millDetail(millId),
    queryFn: () =>
      apiRequest<PublicMillDetailEnvelope>({
        path: `/api/v1/public/mills/${encodeURIComponent(millId)}`,
      }),
    enabled: Boolean(millId),
  });
}

export function usePublicProfile() {
  return useQuery({
    queryKey: queryKeys.public.profile(),
    queryFn: () =>
      apiRequest<PublicProfileEnvelope>({
        path: '/api/v1/public/profile',
      }),
  });
}

export function usePublicNotices() {
  return useQuery({
    queryKey: queryKeys.public.notices(),
    queryFn: () =>
      apiRequest<PublicNoticeListEnvelope>({
        path: '/api/v1/public/notices',
      }),
  });
}
