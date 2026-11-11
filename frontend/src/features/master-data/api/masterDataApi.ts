import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type { components } from '@/lib/api/generated';
import { apiRequest } from '@/lib/api/client';
import { queryKeys } from '@/lib/query/queryKeys';

export type Cooperative = components['schemas']['Cooperative'];
export type Farmer = components['schemas']['Farmer'];
export type Farm = components['schemas']['Farm'];
export type MillCompany = components['schemas']['MillCompany'];
export type Mill = components['schemas']['Mill'];
export type Vehicle = components['schemas']['Vehicle'];
export type Driver = components['schemas']['Driver'];

export type ListEnvelope<T> = {
  readonly success: true;
  readonly data: T[];
  readonly meta: components['schemas']['PaginationMeta'];
  readonly request_id: string;
};

export type SingleEnvelope<T> = {
  readonly success: true;
  readonly data: T;
  readonly meta: components['schemas']['SimpleSuccessMeta'];
  readonly request_id: string;
};

export function useCooperatives() {
  return useQuery({
    queryKey: queryKeys.masterData.cooperatives(),
    queryFn: () => apiRequest<ListEnvelope<Cooperative>>({ path: '/api/v1/cooperatives' }),
  });
}

export function useFarmers(search?: string, enabled = true) {
  return useQuery({
    queryKey: queryKeys.masterData.farmers({ search }),
    queryFn: () =>
      apiRequest<ListEnvelope<Farmer>>({
        path: '/api/v1/farmers',
        query: { q: search?.trim() || undefined, page_size: 50 },
      }),
    enabled,
  });
}

export function useCreateFarmer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: components['schemas']['CreateFarmerRequest']) =>
      apiRequest<SingleEnvelope<Farmer>>({
        path: '/api/v1/farmers',
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.masterData.all });
    },
  });
}

export function useUpdateFarmer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      farmerId,
      payload,
    }: {
      farmerId: string;
      payload: components['schemas']['UpdateFarmerRequest'];
    }) =>
      apiRequest<SingleEnvelope<Farmer>>({
        path: `/api/v1/farmers/${encodeURIComponent(farmerId)}`,
        method: 'PATCH',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.masterData.all });
    },
  });
}

export function useFarms(farmerId?: string) {
  return useQuery({
    queryKey: queryKeys.masterData.farms({ farmerId }),
    queryFn: () =>
      apiRequest<ListEnvelope<Farm>>({
        path: '/api/v1/farms',
        query: { farmer_id: farmerId, page_size: 50 },
      }),
  });
}

export function useCreateFarm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: components['schemas']['CreateFarmRequest']) =>
      apiRequest<SingleEnvelope<Farm>>({
        path: '/api/v1/farms',
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.masterData.all });
    },
  });
}

export function useUpdateFarm() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      farmId,
      payload,
    }: {
      farmId: string;
      payload: components['schemas']['UpdateFarmRequest'];
    }) =>
      apiRequest<SingleEnvelope<Farm>>({
        path: `/api/v1/farms/${encodeURIComponent(farmId)}`,
        method: 'PATCH',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.masterData.all });
    },
  });
}

export function useMillCompanies() {
  return useQuery({
    queryKey: queryKeys.masterData.millCompanies(),
    queryFn: () =>
      apiRequest<ListEnvelope<MillCompany>>({
        path: '/api/v1/mill-companies',
        query: { page_size: 50 },
      }),
  });
}

export function useCreateMillCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: components['schemas']['CreateMillCompanyRequest']) =>
      apiRequest<SingleEnvelope<MillCompany>>({
        path: '/api/v1/mill-companies',
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.masterData.all });
    },
  });
}

export function useMills(search?: string) {
  return useQuery({
    queryKey: queryKeys.masterData.mills({ search }),
    queryFn: () =>
      apiRequest<ListEnvelope<Mill>>({
        path: '/api/v1/mills',
        query: { q: search?.trim() || undefined, page_size: 50 },
      }),
  });
}

export function useCreateMill() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: components['schemas']['CreateMillRequest']) =>
      apiRequest<SingleEnvelope<Mill>>({
        path: '/api/v1/mills',
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.masterData.all });
      void qc.invalidateQueries({ queryKey: queryKeys.public.all });
    },
  });
}

export function useUpdateMill() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      millId,
      payload,
    }: {
      millId: string;
      payload: components['schemas']['UpdateMillRequest'];
    }) =>
      apiRequest<SingleEnvelope<Mill>>({
        path: `/api/v1/mills/${encodeURIComponent(millId)}`,
        method: 'PATCH',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.masterData.all });
      void qc.invalidateQueries({ queryKey: queryKeys.public.all });
    },
  });
}

export function useVehicles() {
  return useQuery({
    queryKey: queryKeys.masterData.vehicles(),
    queryFn: () =>
      apiRequest<ListEnvelope<Vehicle>>({
        path: '/api/v1/vehicles',
        query: { page_size: 50 },
      }),
  });
}

export function useCreateVehicle() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: components['schemas']['CreateVehicleRequest']) =>
      apiRequest<SingleEnvelope<Vehicle>>({
        path: '/api/v1/vehicles',
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.masterData.vehicles() });
    },
  });
}

export function useDrivers() {
  return useQuery({
    queryKey: queryKeys.masterData.drivers(),
    queryFn: () =>
      apiRequest<ListEnvelope<Driver>>({
        path: '/api/v1/drivers',
        query: { page_size: 50 },
      }),
  });
}

export function useCreateDriver() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: components['schemas']['CreateDriverRequest']) =>
      apiRequest<SingleEnvelope<Driver>>({
        path: '/api/v1/drivers',
        method: 'POST',
        body: payload,
      }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: queryKeys.masterData.drivers() });
    },
  });
}
