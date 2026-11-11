import type { RoleCode } from '@/lib/auth/permissions';

export interface NavItem {
  readonly to: string;
  readonly label: string;
}

export const PUBLIC_NAV_ITEMS: readonly NavItem[] = [
  { to: '/', label: 'Beranda' },
  { to: '/harga-tbs', label: 'Harga TBS' },
  { to: '/lokasi-pks', label: 'Lokasi PKS' },
  { to: '/tentang', label: 'Tentang' },
  { to: '/kemitraan', label: 'Kemitraan' },
  { to: '/kontak', label: 'Kontak' },
] as const;

const ROLE_NAV_MAP: Record<RoleCode, readonly NavItem[]> = {
  FARMER: [
    { to: '/app/petani', label: 'Ringkasan Petani' },
    { to: '/app/petani/panen', label: 'Riwayat Panen & Bayar' },
  ],
  COOPERATIVE_OPERATOR: [
    { to: '/app/koperasi', label: 'Beranda & Master Data' },
    { to: '/app/koperasi/penerimaan', label: 'Penerimaan & Timbang TBS' },
    { to: '/app/koperasi/surat-jalan', label: 'Surat Jalan e-DO' },
  ],
  PERUMDA_OPERATIONS: [
    { to: '/app/perumda', label: 'Dashboard & Master PKS' },
    { to: '/app/perumda/harga', label: 'Manajemen Harga PKS' },
    { to: '/app/perumda/kontrak', label: 'Kontrak & Kuota PKS' },
    { to: '/app/perumda/logistik', label: 'Monitoring Logistik e-DO' },
    { to: '/app/perumda/rekonsiliasi', label: 'Rekonsiliasi & Sengketa' },
    { to: '/app/perumda/pembayaran', label: 'Faktur & Pembayaran' },
  ],
  PERUMDA_FINANCE: [
    { to: '/app/perumda/pembayaran', label: 'Faktur & Pembayaran' },
    { to: '/app/perumda/rekonsiliasi', label: 'Rekonsiliasi Terkait' },
    { to: '/app/perumda/kontrak', label: 'Kontrak & Kuota' },
    { to: '/app/perumda', label: 'Ringkasan Operasional' },
  ],
  MILL_OPERATOR: [
    { to: '/app/pks', label: 'Verifikasi Kedatangan e-DO' },
    { to: '/app/pks/tiket-timbang', label: 'Tiket Timbang & Grading' },
  ],
  DIRECTOR: [
    { to: '/app/direksi', label: 'Dashboard Eksekutif' },
    { to: '/app/direksi/persetujuan', label: 'Pusat Persetujuan' },
    { to: '/app/admin/audit', label: 'Audit Trail' },
  ],
  SYSTEM_ADMIN: [
    { to: '/app/admin', label: 'Kesehatan Sistem' },
    { to: '/app/admin/pengguna', label: 'Pengguna & Aturan Versi' },
    { to: '/app/admin/audit', label: 'Audit & CCTV Digital' },
  ],
};

export function getInternalNavItemsForRoles(roles: readonly RoleCode[]): readonly NavItem[] {
  const seen = new Set<string>();
  const collected: NavItem[] = [];
  for (const role of roles) {
    for (const item of ROLE_NAV_MAP[role] ?? []) {
      if (!seen.has(item.to)) {
        seen.add(item.to);
        collected.push(item);
      }
    }
  }
  return collected;
}
