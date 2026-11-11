import { lazy, type ComponentType } from 'react';
import type { AuthenticatedUser } from '@/lib/auth/permissions';
import { RouteFoundationStub } from './RouteFoundationStub';

export interface InternalPageProps {
  readonly user: AuthenticatedUser;
}

const lazyHomePage = lazy(async () => ({
  default: (await import('@/features/public/pages/HomePage')).HomePage,
}));
const lazyHargaTbsPage = lazy(async () => ({
  default: (await import('@/features/public/pages/HargaTbsPage')).HargaTbsPage,
}));
const lazyPksDetailPage = lazy(async () => ({
  default: (await import('@/features/public/pages/PksDetailPage')).PksDetailPage,
}));
const lazyLokasiPksPage = lazy(async () => ({
  default: (await import('@/features/public/pages/LokasiPksPage')).LokasiPksPage,
}));
const lazyTentangPage = lazy(async () => ({
  default: (await import('@/features/public/pages/TentangPage')).TentangPage,
}));
const lazyKemitraanPage = lazy(async () => ({
  default: (await import('@/features/public/pages/KemitraanPage')).KemitraanPage,
}));
const lazyKontakPage = lazy(async () => ({
  default: (await import('@/features/public/pages/KontakPage')).KontakPage,
}));
const lazyLoginPage = lazy(async () => ({
  default: (await import('@/features/auth/pages/LoginPage')).LoginPage,
}));
const lazyKoperasiHomePage = lazy(async () => ({
  default: (await import('@/features/cooperative/pages/KoperasiHomePage')).KoperasiHomePage,
}));
const lazyKoperasiReceivingPage = lazy(async () => ({
  default: (await import('@/features/receiving/pages/KoperasiReceivingPage')).KoperasiReceivingPage,
}));
const lazyKoperasiSuratJalanPage = lazy(async () => ({
  default: (await import('@/features/logistics/pages/KoperasiSuratJalanPage')).KoperasiSuratJalanPage,
}));
const lazyPerumdaDashboardPage = lazy(async () => ({
  default: (await import('@/features/perumda/pages/PerumdaDashboardPage')).PerumdaDashboardPage,
}));
const lazyPerumdaPricingPage = lazy(async () => ({
  default: (await import('@/features/pricing/pages/PerumdaPricingPage')).PerumdaPricingPage,
}));
const lazyPerumdaContractsPage = lazy(async () => ({
  default: (await import('@/features/logistics/pages/PerumdaContractsPage')).PerumdaContractsPage,
}));
const lazyPerumdaLogistikPage = lazy(async () => ({
  default: (await import('@/features/logistics/pages/PerumdaLogistikPage')).PerumdaLogistikPage,
}));
const lazyPerumdaReconciliationPage = lazy(async () => ({
  default: (await import('@/features/reconciliation/pages/PerumdaReconciliationPage'))
    .PerumdaReconciliationPage,
}));
const lazyMillPortalPage = lazy(async () => ({
  default: (await import('@/features/mill/pages/MillOperatorPortalPage')).MillOperatorPortalPage,
}));
const lazyMillTicketsPage = lazy(async () => ({
  default: (await import('@/features/mill/pages/MillTicketsPage')).MillTicketsPage,
}));
const lazyPerumdaFinancePage = lazy(async () => ({
  default: (await import('@/features/finance/pages/PerumdaFinancePage')).PerumdaFinancePage,
}));
const lazyDireksiDashboardPage = lazy(async () => ({
  default: (await import('@/features/director/pages/DireksiDashboardPage')).DireksiDashboardPage,
}));
const lazyDireksiPersetujuanPage = lazy(async () => ({
  default: (await import('@/features/director/pages/DireksiPersetujuanPage')).DireksiPersetujuanPage,
}));
const lazyAdminDashboardPage = lazy(async () => ({
  default: (await import('@/features/admin/pages/AdminDashboardPage')).AdminDashboardPage,
}));
const lazyAdminPenggunaPage = lazy(async () => ({
  default: (await import('@/features/admin/pages/AdminPenggunaPage')).AdminPenggunaPage,
}));
const lazyAdminAuditPage = lazy(async () => ({
  default: (await import('@/features/admin/pages/AdminAuditPage')).AdminAuditPage,
}));
const lazyPetaniDashboardPage = lazy(async () => ({
  default: (await import('@/features/farmer/pages/PetaniDashboardPage')).PetaniDashboardPage,
}));
const lazyPetaniPanenPage = lazy(async () => ({
  default: (await import('@/features/farmer/pages/PetaniPanenPage')).PetaniPanenPage,
}));

export const PUBLIC_AND_AUTH_PAGE_MAP: Record<string, ComponentType> = {
  '/': lazyHomePage,
  '/harga-tbs': lazyHargaTbsPage,
  '/pks/$id': lazyPksDetailPage,
  '/lokasi-pks': lazyLokasiPksPage,
  '/tentang': lazyTentangPage,
  '/kemitraan': lazyKemitraanPage,
  '/kontak': lazyKontakPage,
  '/login': lazyLoginPage,
};

export const INTERNAL_PAGE_MAP: Record<string, ComponentType<InternalPageProps>> = {
  '/app/petani': lazyPetaniDashboardPage,
  '/app/petani/panen': lazyPetaniPanenPage,
  '/app/koperasi': lazyKoperasiHomePage,
  '/app/koperasi/penerimaan': lazyKoperasiReceivingPage,
  '/app/koperasi/surat-jalan': lazyKoperasiSuratJalanPage,
  '/app/perumda': lazyPerumdaDashboardPage,
  '/app/perumda/harga': lazyPerumdaPricingPage,
  '/app/perumda/kontrak': lazyPerumdaContractsPage,
  '/app/perumda/logistik': lazyPerumdaLogistikPage,
  '/app/perumda/rekonsiliasi': lazyPerumdaReconciliationPage,
  '/app/perumda/pembayaran': lazyPerumdaFinancePage,
  '/app/pks': lazyMillPortalPage,
  '/app/pks/tiket-timbang': lazyMillTicketsPage,
  '/app/direksi': lazyDireksiDashboardPage,
  '/app/direksi/persetujuan': lazyDireksiPersetujuanPage,
  '/app/admin': lazyAdminDashboardPage,
  '/app/admin/pengguna': lazyAdminPenggunaPage,
  '/app/admin/audit': lazyAdminAuditPage,
};

export function resolvePublicOrAuthPage(path: string): ComponentType {
  return PUBLIC_AND_AUTH_PAGE_MAP[path] ?? (() => <RouteFoundationStub routePath={path} />);
}

export function resolveInternalPage(path: string): ComponentType<InternalPageProps> {
  return INTERNAL_PAGE_MAP[path] ?? (() => <RouteFoundationStub routePath={path} />);
}
