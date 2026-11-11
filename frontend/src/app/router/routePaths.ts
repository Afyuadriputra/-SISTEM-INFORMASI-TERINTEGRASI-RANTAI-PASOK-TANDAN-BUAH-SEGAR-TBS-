export const PUBLIC_ROUTE_PATHS = [
  '/',
  '/harga-tbs',
  '/pks/$id',
  '/lokasi-pks',
  '/tentang',
  '/kemitraan',
  '/kontak',
] as const;

export const AUTH_ROUTE_PATHS = ['/login'] as const;

export const INTERNAL_ROUTE_PATHS = [
  '/app/petani',
  '/app/petani/panen',
  '/app/koperasi',
  '/app/koperasi/penerimaan',
  '/app/koperasi/surat-jalan',
  '/app/perumda',
  '/app/perumda/harga',
  '/app/perumda/kontrak',
  '/app/perumda/logistik',
  '/app/perumda/rekonsiliasi',
  '/app/perumda/pembayaran',
  '/app/pks',
  '/app/pks/tiket-timbang',
  '/app/direksi',
  '/app/direksi/persetujuan',
  '/app/admin',
  '/app/admin/pengguna',
  '/app/admin/audit',
] as const;

export const ALL_CANONICAL_ROUTE_PATHS = [
  ...PUBLIC_ROUTE_PATHS,
  ...AUTH_ROUTE_PATHS,
  ...INTERNAL_ROUTE_PATHS,
] as const;

export type CanonicalRoutePath = (typeof ALL_CANONICAL_ROUTE_PATHS)[number];
