import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { ListEnvelope, SingleEnvelope } from '@/features/master-data/api/masterDataApi';
import { apiRequest } from '@/lib/api/client';
import type { components } from '@/lib/api/generated';
import { queryKeys } from '@/lib/query/queryKeys';

export type AdminUserSummary = components['schemas']['AdminUserSummary'];
export type CreateUserInput = components['schemas']['CreateUserRequest'];
export type UpdateUserAccessInput = components['schemas']['UpdateUserAccessRequest'];
export type SystemRuleVersion = components['schemas']['SystemRuleVersion'];
export type AuditEvent = components['schemas']['AuditEvent'];
export type SystemObservabilitySummary = components['schemas']['SystemObservabilitySummary'];

export interface CreateRuleVersionInput {
  readonly rule_code: string;
  readonly effective_from: string;
  readonly effective_until?: string | null;
  readonly rule_config: Record<string, unknown>;
  readonly policy_classification: components['schemas']['PolicyClassification'];
  readonly reason?: string | null;
}

export interface AuditFilterInput {
  readonly module?: string;
  readonly request_id?: string;
  readonly date_from?: string;
  readonly date_to?: string;
  readonly page?: number;
}

export function useAdminUsers(search?: string, enabled = true) {
  return useQuery({
    queryKey: queryKeys.admin.users({ q: search ?? '' }),
    queryFn: () =>
      apiRequest<ListEnvelope<AdminUserSummary>>({
        path: '/api/v1/admin/users',
        query: {
          page_size: 50,
          q: search || undefined,
        },
      }),
    enabled,
  });
}

export function useCreateAdminUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateUserInput) =>
      apiRequest<SingleEnvelope<AdminUserSummary>>({
        path: '/api/v1/admin/users',
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.admin.all });
    },
  });
}

export function useUpdateAdminUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, payload }: { userId: string; payload: UpdateUserAccessInput }) =>
      apiRequest<SingleEnvelope<AdminUserSummary>>({
        path: `/api/v1/admin/users/${encodeURIComponent(userId)}`,
        method: 'PATCH',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.admin.all });
    },
  });
}

export function useSystemRuleVersions(enabled = true) {
  return useQuery({
    queryKey: queryKeys.admin.ruleVersions(),
    queryFn: () =>
      apiRequest<ListEnvelope<SystemRuleVersion>>({
        path: '/api/v1/admin/rule-versions',
        query: { page_size: 50 },
      }),
    enabled,
  });
}

export function useCreateSystemRuleVersion() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateRuleVersionInput) =>
      apiRequest<SingleEnvelope<SystemRuleVersion>>({
        path: '/api/v1/admin/rule-versions',
        method: 'POST',
        body: payload as unknown as components['schemas']['CreateSystemRuleVersionRequest'],
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.admin.all });
    },
  });
}

export function useAuditEvents(filter?: AuditFilterInput, enabled = true) {
  return useQuery({
    queryKey: queryKeys.admin.auditEvents(filter as Record<string, unknown>),
    queryFn: () =>
      apiRequest<ListEnvelope<AuditEvent>>({
        path: '/api/v1/admin/audit-events',
        query: {
          page: filter?.page ?? 1,
          page_size: 50,
          module: filter?.module || undefined,
          request_id: filter?.request_id || undefined,
          date_from: filter?.date_from || undefined,
          date_to: filter?.date_to || undefined,
        },
      }),
    enabled,
  });
}

export function useSystemHealthSummary(enabled = true) {
  return useQuery({
    queryKey: queryKeys.admin.systemHealth(),
    queryFn: () =>
      apiRequest<SingleEnvelope<SystemObservabilitySummary>>({
        path: '/api/v1/admin/system-health',
      }),
    enabled,
  });
}
