import { http } from 'msw';
import type { AuthenticatedUser } from '@/lib/auth/permissions';
import { mockDb } from '../mockDb';
import {
  appendMockAuditEvent,
  assertMockCsrf,
  makeErrorResponse,
  makePaginatedEnvelope,
  makeSimpleEnvelope,
  requireMockPermission,
} from '../utils';

function getCooperativeScopeId(user: AuthenticatedUser): string | null {
  const scope = user.access_scopes.find((s) => s.scope_type === 'COOPERATIVE');
  return scope?.cooperative_id ?? null;
}

function validatePairedCoords(lat?: string | null, lon?: string | null): boolean {
  const hasLat = lat !== undefined && lat !== null && lat.trim() !== '';
  const hasLon = lon !== undefined && lon !== null && lon.trim() !== '';
  if (hasLat !== hasLon) {
    return false;
  }
  if (!hasLat) {
    return true;
  }
  const latNum = Number(lat);
  const lonNum = Number(lon);
  return (
    Number.isFinite(latNum) &&
    Number.isFinite(lonNum) &&
    latNum >= -90 &&
    latNum <= 90 &&
    lonNum >= -180 &&
    lonNum <= 180
  );
}

export const masterDataHandlers = [
  http.get('/api/v1/cooperatives', ({ request }) => {
    const auth = requireMockPermission('cooperatives.read');
    if ('error' in auth) return auth.error;
    const url = new URL(request.url);
    const coopScope = getCooperativeScopeId(auth.user);
    const items = coopScope
      ? mockDb.cooperatives.filter((c) => c.id === coopScope)
      : mockDb.cooperatives;
    return makePaginatedEnvelope(items, url);
  }),

  http.get('/api/v1/farmers', ({ request }) => {
    const auth = requireMockPermission('farmers.read');
    if ('error' in auth) return auth.error;
    const url = new URL(request.url);
    const search = (url.searchParams.get('q') ?? url.searchParams.get('search') ?? '')
      .trim()
      .toLowerCase();
    const coopScope = getCooperativeScopeId(auth.user);
    const farmerScope = auth.user.access_scopes.find((s) => s.scope_type === 'FARMER')?.farmer_id;

    let items = mockDb.farmers;
    if (coopScope) {
      items = items.filter((f) => f.cooperative_id === coopScope);
    }
    if (farmerScope) {
      items = items.filter((f) => f.id === farmerScope);
    }
    if (search) {
      items = items.filter(
        (f) =>
          f.full_name.toLowerCase().includes(search) ||
          f.farmer_code.toLowerCase().includes(search),
      );
    }
    return makePaginatedEnvelope(items, url);
  }),

  http.post('/api/v1/farmers', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('farmers.write');
    if ('error' in auth) return auth.error;

    const body = (await request.json().catch(() => null)) as {
      farmer_code?: string;
      full_name?: string;
      contact_phone?: string | null;
      cooperative_id?: string;
      membership_number?: string | null;
    } | null;

    if (!body?.farmer_code || !body?.full_name || !body?.cooperative_id) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }
    const coopScope = getCooperativeScopeId(auth.user);
    if (coopScope && body.cooperative_id !== coopScope) {
      return makeErrorResponse('AUTH_SCOPE_FORBIDDEN');
    }
    if (mockDb.farmers.some((f) => f.farmer_code.toLowerCase() === body.farmer_code!.toLowerCase())) {
      return makeErrorResponse('MD_DUPLICATE_CODE');
    }

    const now = new Date().toISOString();
    const newFarmer = {
      id: `40000000-0000-4000-8000-${String(mockDb.farmers.length + 101).padStart(12, '0')}`,
      party_id: `10000000-0000-4000-8000-${String(mockDb.farmers.length + 501).padStart(12, '0')}`,
      farmer_code: body.farmer_code.trim(),
      full_name: body.full_name.trim(),
      contact_phone: body.contact_phone ?? '',
      cooperative_id: body.cooperative_id,
      membership_number: body.membership_number ?? '',
      status: 'ACTIVE' as const,
      version: 1,
      created_at: now,
      updated_at: now,
    };
    mockDb.farmers.unshift(newFarmer);
    appendMockAuditEvent({
      actor: auth.user,
      action: 'FARMER_CREATED',
      entityType: 'farmers',
      entityId: newFarmer.id,
      summary: `Petani baru terdaftar: ${newFarmer.farmer_code}`,
    });
    return makeSimpleEnvelope(newFarmer, undefined, 201);
  }),

  http.get('/api/v1/farmers/:farmerId', ({ params }) => {
    const auth = requireMockPermission('farmers.read');
    if ('error' in auth) return auth.error;
    const farmer = mockDb.farmers.find((f) => f.id === String(params.farmerId));
    if (!farmer) {
      return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    }
    const coopScope = getCooperativeScopeId(auth.user);
    if (coopScope && farmer.cooperative_id !== coopScope) {
      return makeErrorResponse('AUTH_SCOPE_FORBIDDEN');
    }
    const farmerScope = auth.user.access_scopes.find((s) => s.scope_type === 'FARMER')?.farmer_id;
    if (farmerScope && farmer.id !== farmerScope) {
      return makeErrorResponse('AUTH_SCOPE_FORBIDDEN');
    }
    return makeSimpleEnvelope(farmer);
  }),

  http.patch('/api/v1/farmers/:farmerId', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('farmers.write');
    if ('error' in auth) return auth.error;

    const index = mockDb.farmers.findIndex((f) => f.id === String(params.farmerId));
    if (index === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.farmers[index];
    const coopScope = getCooperativeScopeId(auth.user);
    if (coopScope && current.cooperative_id !== coopScope) {
      return makeErrorResponse('AUTH_SCOPE_FORBIDDEN');
    }

    const body = (await request.json().catch(() => null)) as {
      full_name?: string;
      contact_phone?: string | null;
      status?: 'ACTIVE' | 'INACTIVE';
      reason?: string | null;
      version?: number;
    } | null;

    if (!body || typeof body.version !== 'number') {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }
    if (body.version !== current.version) {
      return makeErrorResponse('MD_STALE_RECORD_VERSION');
    }
    const updated = {
      ...current,
      full_name: body.full_name?.trim() || current.full_name,
      contact_phone: body.contact_phone ?? current.contact_phone,
      status: body.status ?? current.status,
      version: current.version + 1,
      updated_at: new Date().toISOString(),
    };
    mockDb.farmers[index] = updated;
    appendMockAuditEvent({
      actor: auth.user,
      action: 'FARMER_UPDATED',
      entityType: 'farmers',
      entityId: updated.id,
      summary: `Data petani diperbarui (${updated.farmer_code}): ${body.reason ?? 'Pembaruan profil'}`,
    });
    return makeSimpleEnvelope(updated);
  }),

  http.get('/api/v1/farms', ({ request }) => {
    const auth = requireMockPermission('farms.read');
    if ('error' in auth) return auth.error;
    const url = new URL(request.url);
    const farmerId = url.searchParams.get('farmer_id');
    const coopScope = getCooperativeScopeId(auth.user);
    const farmerScope = auth.user.access_scopes.find((s) => s.scope_type === 'FARMER')?.farmer_id;

    let items = mockDb.farms;
    if (farmerId) {
      items = items.filter((f) => f.farmer_id === farmerId);
    }
    if (coopScope) {
      const allowedFarmerIds = new Set(
        mockDb.farmers.filter((fm) => fm.cooperative_id === coopScope).map((fm) => fm.id),
      );
      items = items.filter((f) => allowedFarmerIds.has(f.farmer_id));
    }
    if (farmerScope) {
      items = items.filter((f) => f.farmer_id === farmerScope);
    }
    return makePaginatedEnvelope(items, url);
  }),

  http.post('/api/v1/farms', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('farms.write');
    if ('error' in auth) return auth.error;

    const body = (await request.json().catch(() => null)) as {
      farmer_id?: string;
      farm_code?: string;
      farm_name?: string;
      area_hectares?: string;
      planting_year?: number | null;
      stdb_number?: string | null;
      village?: string | null;
      district?: string | null;
      latitude?: string | null;
      longitude?: string | null;
    } | null;

    if (!body?.farmer_id || !body?.farm_code || !body?.farm_name || !body?.area_hectares) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }
    if (!validatePairedCoords(body.latitude, body.longitude)) {
      return makeErrorResponse('VAL_INVALID_COORDINATES');
    }
    const farmer = mockDb.farmers.find((fm) => fm.id === body.farmer_id);
    if (!farmer) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const coopScope = getCooperativeScopeId(auth.user);
    if (coopScope && farmer.cooperative_id !== coopScope) {
      return makeErrorResponse('AUTH_SCOPE_FORBIDDEN');
    }
    if (mockDb.farms.some((f) => f.farm_code.toLowerCase() === body.farm_code!.toLowerCase())) {
      return makeErrorResponse('MD_DUPLICATE_CODE');
    }

    const now = new Date().toISOString();
    const hasCoords = Boolean(body.latitude && body.longitude);
    const newFarm = {
      id: `40000000-0000-4000-8000-${String(mockDb.farms.length + 201).padStart(12, '0')}`,
      farmer_id: body.farmer_id,
      farm_code: body.farm_code.trim(),
      farm_name: body.farm_name.trim(),
      area_hectares: Number(body.area_hectares).toFixed(4),
      planting_year: body.planting_year ?? 2018,
      stdb_number: body.stdb_number ?? '',
      village: body.village ?? '',
      district: body.district ?? '',
      latitude: hasCoords ? (body.latitude ?? null) : null,
      longitude: hasCoords ? (body.longitude ?? null) : null,
      verification_status: hasCoords ? ('VERIFIED' as const) : ('UNVERIFIED' as const),
      is_public_location: false as const,
      version: 1,
      created_at: now,
      updated_at: now,
    };
    mockDb.farms.unshift(newFarm);
    appendMockAuditEvent({
      actor: auth.user,
      action: 'FARM_CREATED',
      entityType: 'farms',
      entityId: newFarm.id,
      summary: `Kebun baru terdaftar: ${newFarm.farm_code}`,
    });
    return makeSimpleEnvelope(newFarm, undefined, 201);
  }),

  http.patch('/api/v1/farms/:farmId', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('farms.write');
    if ('error' in auth) return auth.error;

    const idx = mockDb.farms.findIndex((f) => f.id === String(params.farmId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.farms[idx];
    const body = (await request.json().catch(() => null)) as {
      farm_name?: string;
      area_hectares?: string;
      planting_year?: number | null;
      stdb_number?: string | null;
      village?: string | null;
      district?: string | null;
      latitude?: string | null;
      longitude?: string | null;
      version?: number;
    } | null;

    if (!body || typeof body.version !== 'number') {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }
    if (body.version !== current.version) {
      return makeErrorResponse('MD_STALE_RECORD_VERSION');
    }
    if (!validatePairedCoords(body.latitude, body.longitude)) {
      return makeErrorResponse('VAL_INVALID_COORDINATES');
    }
    const updated = {
      ...current,
      farm_name: body.farm_name ?? current.farm_name,
      area_hectares: body.area_hectares ? Number(body.area_hectares).toFixed(4) : current.area_hectares,
      planting_year: body.planting_year ?? current.planting_year,
      stdb_number: body.stdb_number ?? current.stdb_number,
      village: body.village ?? current.village,
      district: body.district ?? current.district,
      latitude: body.latitude ?? current.latitude,
      longitude: body.longitude ?? current.longitude,
      version: current.version + 1,
      updated_at: new Date().toISOString(),
    };
    mockDb.farms[idx] = updated;
    return makeSimpleEnvelope(updated);
  }),

  http.get('/api/v1/mill-companies', ({ request }) => {
    const auth = requireMockPermission('mills.read');
    if ('error' in auth) return auth.error;
    return makePaginatedEnvelope(mockDb.millCompanies, new URL(request.url));
  }),

  http.post('/api/v1/mill-companies', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('mills.write');
    if ('error' in auth) return auth.error;
    const body = (await request.json().catch(() => null)) as {
      company_code?: string;
      company_name?: string;
      contact_phone?: string | null;
      address?: string | null;
    } | null;
    if (!body?.company_code || !body?.company_name) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }
    if (mockDb.millCompanies.some((c) => c.company_code === body.company_code)) {
      return makeErrorResponse('MD_DUPLICATE_CODE');
    }
    const created = {
      id: `30000000-0000-4000-8000-${String(mockDb.millCompanies.length + 901).padStart(12, '0')}`,
      party_id: `10000000-0000-4000-8000-${String(mockDb.millCompanies.length + 901).padStart(12, '0')}`,
      company_code: body.company_code.trim(),
      company_name: body.company_name.trim(),
      contact_phone: body.contact_phone ?? '',
      address: body.address ?? '',
      status: 'ACTIVE' as const,
      created_at: new Date().toISOString(),
    };
    mockDb.millCompanies.unshift(created as (typeof mockDb.millCompanies)[number]);
    return makeSimpleEnvelope(created, undefined, 201);
  }),

  http.get('/api/v1/mills', ({ request }) => {
    const auth = requireMockPermission('mills.read');
    if ('error' in auth) return auth.error;
    const url = new URL(request.url);
    const search = (url.searchParams.get('q') ?? url.searchParams.get('search') ?? '')
      .trim()
      .toLowerCase();
    const millScope = auth.user.access_scopes.find((s) => s.scope_type === 'MILL')?.mill_id;
    let items = mockDb.mills;
    if (millScope) {
      items = items.filter((m) => m.id === millScope);
    }
    if (search) {
      items = items.filter(
        (m) =>
          m.mill_name.toLowerCase().includes(search) ||
          m.mill_code.toLowerCase().includes(search),
      );
    }
    return makePaginatedEnvelope(items, url);
  }),

  http.post('/api/v1/mills', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('mills.write');
    if ('error' in auth) return auth.error;
    const body = (await request.json().catch(() => null)) as {
      mill_company_id?: string;
      mill_code?: string;
      mill_name?: string;
      address?: string;
      district?: string | null;
      regency?: string;
      province?: string;
      latitude?: string | null;
      longitude?: string | null;
      contact_phone?: string | null;
      partnership_status?: string;
      is_public?: boolean;
    } | null;

    if (!body?.mill_company_id || !body?.mill_code || !body?.mill_name || !body?.address || !body?.regency) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }
    if (!validatePairedCoords(body.latitude, body.longitude)) {
      return makeErrorResponse('VAL_INVALID_COORDINATES');
    }
    if (mockDb.mills.some((m) => m.mill_code.toLowerCase() === body.mill_code!.toLowerCase())) {
      return makeErrorResponse('MD_DUPLICATE_CODE');
    }
    const company = mockDb.millCompanies.find((c) => c.id === body.mill_company_id);
    const hasCoords = Boolean(body.latitude && body.longitude);
    const now = new Date().toISOString();
    const created = {
      id: `30000000-0000-4000-8000-${String(mockDb.mills.length + 10).padStart(12, '0')}`,
      mill_company_id: body.mill_company_id,
      company_name: company?.company_name ?? 'Perusahaan PKS Mitra',
      mill_code: body.mill_code.trim(),
      mill_name: body.mill_name.trim(),
      address: body.address.trim(),
      district: body.district ?? '',
      regency: body.regency.trim(),
      province: body.province ?? 'Riau',
      latitude: hasCoords ? body.latitude! : null,
      longitude: hasCoords ? body.longitude! : null,
      has_verified_coordinates: hasCoords,
      contact_phone: body.contact_phone ?? null,
      partnership_status: (body.partnership_status ?? 'ACTIVE') as 'ACTIVE',
      is_public: Boolean(body.is_public),
      location_verified_at: hasCoords ? now : null,
      version: 1,
      created_at: now,
      updated_at: now,
    };
    mockDb.mills.unshift(created as (typeof mockDb.mills)[number]);
    appendMockAuditEvent({
      actor: auth.user,
      action: 'MILL_CREATED',
      entityType: 'mills',
      entityId: created.id,
      summary: `PKS mitra ditambahkan (${created.mill_code}, publik=${String(created.is_public)})`,
    });
    return makeSimpleEnvelope(created, undefined, 201);
  }),

  http.patch('/api/v1/mills/:millId', async ({ params, request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('mills.write');
    if ('error' in auth) return auth.error;
    const idx = mockDb.mills.findIndex((m) => m.id === String(params.millId));
    if (idx === -1) return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    const current = mockDb.mills[idx];
    const body = (await request.json().catch(() => null)) as {
      mill_name?: string;
      address?: string;
      district?: string | null;
      regency?: string;
      latitude?: string | null;
      longitude?: string | null;
      contact_phone?: string | null;
      partnership_status?: string;
      is_public?: boolean;
      version?: number;
    } | null;
    if (!body || typeof body.version !== 'number') {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }
    if (body.version !== current.version) {
      return makeErrorResponse('MD_STALE_RECORD_VERSION');
    }
    const nextLat = body.latitude !== undefined ? body.latitude : current.latitude;
    const nextLon = body.longitude !== undefined ? body.longitude : current.longitude;
    if (!validatePairedCoords(nextLat, nextLon)) {
      return makeErrorResponse('VAL_INVALID_COORDINATES');
    }
    const hasCoords = Boolean(nextLat && nextLon);
    const now = new Date().toISOString();
    const updated = {
      ...current,
      mill_name: body.mill_name ?? current.mill_name,
      address: body.address ?? current.address,
      district: body.district ?? current.district,
      regency: body.regency ?? current.regency,
      latitude: hasCoords ? (nextLat ?? null) : null,
      longitude: hasCoords ? (nextLon ?? null) : null,
      has_verified_coordinates: hasCoords,
      contact_phone: body.contact_phone !== undefined ? body.contact_phone : current.contact_phone,
      partnership_status: (body.partnership_status ?? current.partnership_status) as 'ACTIVE' | 'INACTIVE',
      is_public: body.is_public !== undefined ? body.is_public : current.is_public,
      location_verified_at: hasCoords ? now : null,
      version: current.version + 1,
      updated_at: now,
    };
    mockDb.mills[idx] = updated;
    appendMockAuditEvent({
      actor: auth.user,
      action: 'MILL_UPDATED',
      entityType: 'mills',
      entityId: updated.id,
      summary: `Profil PKS diperbarui (${updated.mill_code}, publik=${String(updated.is_public)})`,
    });
    return makeSimpleEnvelope(updated);
  }),

  http.get('/api/v1/vehicles', ({ request }) => {
    const auth = requireMockPermission('vehicles.read');
    if ('error' in auth) return auth.error;
    return makePaginatedEnvelope(mockDb.vehicles, new URL(request.url));
  }),

  http.post('/api/v1/vehicles', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('vehicles.write');
    if ('error' in auth) return auth.error;
    const body = (await request.json().catch(() => null)) as {
      plate_number?: string;
      vehicle_type?: string;
      nominal_capacity_kg?: string;
    } | null;
    if (!body?.plate_number || !body?.vehicle_type || !body?.nominal_capacity_kg) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }
    const created = {
      id: `40000000-0000-4000-8000-${String(mockDb.vehicles.length + 701).padStart(12, '0')}`,
      plate_number: body.plate_number.trim().toUpperCase(),
      vehicle_type: body.vehicle_type.trim(),
      nominal_capacity_kg: Number(body.nominal_capacity_kg).toFixed(3),
      status: 'ACTIVE' as const,
    };
    mockDb.vehicles.unshift(created as (typeof mockDb.vehicles)[number]);
    return makeSimpleEnvelope(created, undefined, 201);
  }),

  http.get('/api/v1/drivers', ({ request }) => {
    const auth = requireMockPermission('drivers.read');
    if ('error' in auth) return auth.error;
    return makePaginatedEnvelope(mockDb.drivers, new URL(request.url));
  }),

  http.post('/api/v1/drivers', async ({ request }) => {
    const csrfError = assertMockCsrf(request);
    if (csrfError) return csrfError;
    const auth = requireMockPermission('drivers.write');
    if ('error' in auth) return auth.error;
    const body = (await request.json().catch(() => null)) as {
      full_name?: string;
      contact_phone?: string | null;
      driver_reference?: string | null;
    } | null;
    if (!body?.full_name) {
      return makeErrorResponse('VAL_REQUIRED_FIELD');
    }
    const created = {
      id: `40000000-0000-4000-8000-${String(mockDb.drivers.length + 801).padStart(12, '0')}`,
      full_name: body.full_name.trim(),
      contact_phone: body.contact_phone ?? '',
      driver_reference: body.driver_reference ?? `DRV-${mockDb.drivers.length + 1}`,
      status: 'ACTIVE' as const,
    };
    mockDb.drivers.unshift(created as (typeof mockDb.drivers)[number]);
    return makeSimpleEnvelope(created, undefined, 201);
  }),
];
