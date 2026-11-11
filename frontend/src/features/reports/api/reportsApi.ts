import { useQuery } from '@tanstack/react-query';
import type { SingleEnvelope } from '@/features/master-data/api/masterDataApi';
import { apiRequest } from '@/lib/api/client';
import type { components } from '@/lib/api/generated';
import { queryKeys } from '@/lib/query/queryKeys';

export type OverviewReport = components['schemas']['OverviewReport'];
export type SupplyReport = components['schemas']['SupplyReport'];
export type ReconciliationReport = components['schemas']['ReconciliationReport'];
export type FinanceReport = components['schemas']['FinanceReport'];

export interface ReportDateFilter {
  readonly date_from?: string;
  readonly date_to?: string;
}

export function useOverviewReport(filter?: ReportDateFilter, enabled = true) {
  return useQuery({
    queryKey: queryKeys.reports.overview(filter as Record<string, unknown>),
    queryFn: () =>
      apiRequest<SingleEnvelope<OverviewReport>>({
        path: '/api/v1/reports/overview',
        query: {
          date_from: filter?.date_from || undefined,
          date_to: filter?.date_to || undefined,
        },
      }),
    enabled,
  });
}

export function useSupplyReport(
  filter?: ReportDateFilter & { readonly mill_id?: string },
  enabled = true,
) {
  return useQuery({
    queryKey: queryKeys.reports.supply(filter as Record<string, unknown>),
    queryFn: () =>
      apiRequest<SingleEnvelope<SupplyReport>>({
        path: '/api/v1/reports/supply',
        query: {
          date_from: filter?.date_from || undefined,
          date_to: filter?.date_to || undefined,
          mill_id: filter?.mill_id || undefined,
        },
      }),
    enabled,
  });
}

export function useReconciliationReport(filter?: ReportDateFilter, enabled = true) {
  return useQuery({
    queryKey: queryKeys.reports.reconciliation(filter as Record<string, unknown>),
    queryFn: () =>
      apiRequest<SingleEnvelope<ReconciliationReport>>({
        path: '/api/v1/reports/reconciliation',
        query: {
          date_from: filter?.date_from || undefined,
          date_to: filter?.date_to || undefined,
        },
      }),
    enabled,
  });
}

export function useFinanceReport(filter?: ReportDateFilter, enabled = true) {
  return useQuery({
    queryKey: queryKeys.reports.finance(filter as Record<string, unknown>),
    queryFn: () =>
      apiRequest<SingleEnvelope<FinanceReport>>({
        path: '/api/v1/reports/finance',
        query: {
          date_from: filter?.date_from || undefined,
          date_to: filter?.date_to || undefined,
        },
      }),
    enabled,
  });
}
