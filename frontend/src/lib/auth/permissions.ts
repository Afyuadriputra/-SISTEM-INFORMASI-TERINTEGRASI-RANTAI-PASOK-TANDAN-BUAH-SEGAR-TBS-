import type { components } from '@/lib/api/generated';

export type RoleCode = components['schemas']['RoleCode'];
export type ScopeType = components['schemas']['ScopeType'];
export type AuthenticatedUser = components['schemas']['AuthenticatedUser'];
export type AccessScopeGrant = components['schemas']['AccessScopeGrant'];

export const ALL_ROLE_CODES = [
  'FARMER',
  'COOPERATIVE_OPERATOR',
  'PERUMDA_OPERATIONS',
  'PERUMDA_FINANCE',
  'MILL_OPERATOR',
  'DIRECTOR',
  'SYSTEM_ADMIN',
] as const satisfies readonly RoleCode[];

export const ROLE_LABELS: Record<RoleCode, string> = {
  FARMER: 'Petani Swadaya',
  COOPERATIVE_OPERATOR: 'Operator Koperasi',
  PERUMDA_OPERATIONS: 'Staf Operasional Perumda',
  PERUMDA_FINANCE: 'Staf Keuangan Perumda',
  MILL_OPERATOR: 'Petugas PKS',
  DIRECTOR: 'Direksi Perumda',
  SYSTEM_ADMIN: 'Administrator Sistem',
};

export const ROLE_HOME_PATHS: Record<RoleCode, string> = {
  FARMER: '/app/petani',
  COOPERATIVE_OPERATOR: '/app/koperasi',
  PERUMDA_OPERATIONS: '/app/perumda',
  PERUMDA_FINANCE: '/app/perumda/pembayaran',
  MILL_OPERATOR: '/app/pks',
  DIRECTOR: '/app/direksi',
  SYSTEM_ADMIN: '/app/admin',
};

export interface CanonicalRouteMeta {
  readonly path: string;
  readonly label: string;
  readonly access: 'public' | 'auth' | 'internal';
  readonly allowedRoles: readonly RoleCode[];
  readonly requiredPermission?: string;
}

/**
 * Canonical 26 routes defined in AFD section 36 & M0.1 Handoff.
 */
export const CANONICAL_ROUTES: readonly CanonicalRouteMeta[] = [
  { path: '/', label: 'Beranda', access: 'public', allowedRoles: [] },
  { path: '/harga-tbs', label: 'Harga TBS Multi-PKS', access: 'public', allowedRoles: [] },
  { path: '/pks/$id', label: 'Detail Harga & Profil PKS', access: 'public', allowedRoles: [] },
  { path: '/lokasi-pks', label: 'Lokasi Kantor & PKS Mitra', access: 'public', allowedRoles: [] },
  { path: '/tentang', label: 'Tentang Perumda', access: 'public', allowedRoles: [] },
  { path: '/kemitraan', label: 'Informasi Kemitraan', access: 'public', allowedRoles: [] },
  { path: '/kontak', label: 'Kontak Resmi', access: 'public', allowedRoles: [] },
  { path: '/login', label: 'Masuk Portal Internal', access: 'auth', allowedRoles: [] },
  { path: '/app/petani', label: 'Ringkasan Petani', access: 'internal', allowedRoles: ['FARMER'] },
  {
    path: '/app/petani/panen',
    label: 'Riwayat Panen & Pembayaran',
    access: 'internal',
    allowedRoles: ['FARMER'],
  },
  {
    path: '/app/koperasi',
    label: 'Dashboard & Master Data Koperasi',
    access: 'internal',
    allowedRoles: ['COOPERATIVE_OPERATOR'],
  },
  {
    path: '/app/koperasi/penerimaan',
    label: 'Penerimaan, Timbang & Grading TBS',
    access: 'internal',
    allowedRoles: ['COOPERATIVE_OPERATOR'],
  },
  {
    path: '/app/koperasi/surat-jalan',
    label: 'Manajemen e-DO Koperasi',
    access: 'internal',
    allowedRoles: ['COOPERATIVE_OPERATOR'],
  },
  {
    path: '/app/perumda',
    label: 'Dashboard Operasional & PKS',
    access: 'internal',
    allowedRoles: ['PERUMDA_OPERATIONS', 'PERUMDA_FINANCE'],
  },
  {
    path: '/app/perumda/harga',
    label: 'Manajemen Harga Multi-PKS',
    access: 'internal',
    allowedRoles: ['PERUMDA_OPERATIONS', 'PERUMDA_FINANCE'],
  },
  {
    path: '/app/perumda/kontrak',
    label: 'Kontrak & Kuota PKS',
    access: 'internal',
    allowedRoles: ['PERUMDA_OPERATIONS', 'PERUMDA_FINANCE'],
  },
  {
    path: '/app/perumda/logistik',
    label: 'Pengiriman & Logistik e-DO',
    access: 'internal',
    allowedRoles: ['PERUMDA_OPERATIONS', 'PERUMDA_FINANCE'],
  },
  {
    path: '/app/perumda/rekonsiliasi',
    label: 'Rekonsiliasi & Sengketa Berat',
    access: 'internal',
    allowedRoles: ['PERUMDA_OPERATIONS', 'PERUMDA_FINANCE'],
  },
  {
    path: '/app/perumda/pembayaran',
    label: 'Faktur & Pencatatan Pembayaran',
    access: 'internal',
    allowedRoles: ['PERUMDA_FINANCE', 'PERUMDA_OPERATIONS'],
  },
  {
    path: '/app/pks',
    label: 'Dashboard & Verifikasi e-DO PKS',
    access: 'internal',
    allowedRoles: ['MILL_OPERATOR'],
  },
  {
    path: '/app/pks/tiket-timbang',
    label: 'Tiket Timbang & Grading PKS',
    access: 'internal',
    allowedRoles: ['MILL_OPERATOR'],
  },
  {
    path: '/app/direksi',
    label: 'Dashboard Eksekutif Direksi',
    access: 'internal',
    allowedRoles: ['DIRECTOR'],
  },
  {
    path: '/app/direksi/persetujuan',
    label: 'Pusat Persetujuan Direksi',
    access: 'internal',
    allowedRoles: ['DIRECTOR'],
  },
  {
    path: '/app/admin',
    label: 'Dashboard Administrator Sistem',
    access: 'internal',
    allowedRoles: ['SYSTEM_ADMIN'],
  },
  {
    path: '/app/admin/pengguna',
    label: 'Pengguna, Peran & Aturan Versi',
    access: 'internal',
    allowedRoles: ['SYSTEM_ADMIN'],
  },
  {
    path: '/app/admin/audit',
    label: 'Audit Trail & CCTV Digital',
    access: 'internal',
    allowedRoles: ['SYSTEM_ADMIN', 'DIRECTOR'],
  },
] as const;

export function isNonApproverAdmin(user: AuthenticatedUser | null | undefined): boolean {
  if (!user) {
    return false;
  }
  return user.non_approver_admin || user.roles.includes('SYSTEM_ADMIN');
}

export function hasPermission(user: AuthenticatedUser | null | undefined, permission: string): boolean {
  if (!user) {
    return false;
  }
  return user.permissions.includes(permission);
}

export function hasAnyRole(
  user: AuthenticatedUser | null | undefined,
  allowedRoles: readonly RoleCode[],
): boolean {
  if (!user) {
    return false;
  }
  return allowedRoles.some((role) => user.roles.includes(role));
}

export function getRoleHomePath(user: AuthenticatedUser | null | undefined): string {
  if (!user || user.roles.length === 0) {
    return '/login';
  }
  const primaryRole = user.roles[0];
  return ROLE_HOME_PATHS[primaryRole] ?? '/login';
}

export function canAccessRoutePath(
  user: AuthenticatedUser | null | undefined,
  pathname: string,
): boolean {
  const normalized = pathname.startsWith('/pks/') ? '/pks/$id' : pathname;
  const route = CANONICAL_ROUTES.find((entry) => entry.path === normalized);
  if (!route) {
    return false;
  }
  if (route.access === 'public' || route.access === 'auth') {
    return true;
  }
  if (!user) {
    return false;
  }
  return hasAnyRole(user, route.allowedRoles);
}
