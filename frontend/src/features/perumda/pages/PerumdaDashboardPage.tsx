import { Link } from '@tanstack/react-router';
import { useState } from 'react';
import { Button } from '@/components/atoms';
import { KPIGrid, type KPIItem } from '@/components/organisms';
import { DashboardTemplate } from '@/components/templates';
import { FarmerFarmSection } from '@/features/master-data/components/FarmerFarmSection';
import { FleetMasterSection } from '@/features/master-data/components/FleetMasterSection';
import { MillMasterSection } from '@/features/master-data/components/MillMasterSection';
import { useCooperatives, useFarmers, useMills } from '@/features/master-data/api/masterDataApi';
import { useOverviewReport, useReconciliationReport } from '@/features/reports/api/reportsApi';
import { hasPermission, type AuthenticatedUser } from '@/lib/auth/permissions';
import { formatKg } from '@/lib/decimal/precision';

export function PerumdaDashboardPage({ user }: { readonly user: AuthenticatedUser }) {
  const [activeTab, setActiveTab] = useState<'pks' | 'petani' | 'armada'>('pks');
  const canReadFarmers = hasPermission(user, 'farmers.read');
  const canReadReports = hasPermission(user, 'reports.operational.read');
  const millsQuery = useMills();
  const coopsQuery = useCooperatives();
  const farmersQuery = useFarmers(undefined, canReadFarmers);
  const overviewQuery = useOverviewReport(undefined, canReadReports);
  const reconQuery = useReconciliationReport(undefined, canReadReports);

  const canWriteMills = hasPermission(user, 'mills.write');
  const canWriteFarmers = hasPermission(user, 'farmers.write');
  const overview = overviewQuery.data?.data;
  const recon = reconQuery.data?.data;

  const kpis: KPIItem[] = [
    {
      id: 'p-mills',
      label: 'Total PKS Mitra',
      value: String(millsQuery.data?.meta.total_items ?? 0),
      hint: `${(millsQuery.data?.data ?? []).filter((m) => m.is_public).length} disetujui is_public`,
    },
    {
      id: 'p-coops',
      label: 'Koperasi & e-DO Aktif',
      value: `${coopsQuery.data?.meta.total_items ?? 0} | ${overview?.active_deliveries_count ?? 0}`,
      hint: 'Koperasi terhubung | Pengiriman aktif',
    },
    {
      id: 'p-volume',
      label: 'Tonase Terima & Sengketa',
      value: overview ? formatKg(overview.total_received_weight_kg) : '-',
      tone: (recon?.dispute_hold_count ?? 0) > 0 ? 'warning' : 'primary',
      hint: `${recon?.dispute_hold_count ?? 0} sengketa tertahan`,
    },
    {
      id: 'p-farmers',
      label: canReadFarmers ? 'Petani Terdata' : 'Rekonsiliasi Cocok',
      value: canReadFarmers
        ? String(farmersQuery.data?.meta.total_items ?? 0)
        : String(overview?.matched_reconciliations_count ?? 0),
      tone: 'primary',
      hint: canReadFarmers ? 'Tercakup di unit koperasi' : 'Siap proses penagihan',
    },
  ];

  return (
    <DashboardTemplate
      user={user}
      header={{
        eyebrow: 'PORTAL PERUMDA | OPERASIONAL & FLOW-06',
        title: 'Dashboard Operasional & Master Data PKS',
        description:
          'Pusat kendali operasional harian Perumda Unit Agro Niaga beserta pengelolaan master PKS mitra, koperasi, petani, dan publikasi profil.',
        actions: (
          <>
            <Link
              to="/app/perumda/harga"
              className="inline-flex min-h-[44px] items-center rounded-md bg-primary-default px-4 text-sm font-semibold text-primary-foreground hover:bg-brand-hover"
            >
              Kelola Harga PKS
            </Link>
            <Link
              to="/app/perumda/kontrak"
              className="inline-flex min-h-[44px] items-center rounded-md border border-border-control bg-surface-default px-4 text-sm font-semibold text-ink-primary hover:bg-surface-subtle"
            >
              Kontrak & Kuota
            </Link>
            <Link
              to="/app/perumda/rekonsiliasi"
              className="inline-flex min-h-[44px] items-center rounded-md border border-border-control bg-surface-default px-4 text-sm font-semibold text-ink-primary hover:bg-surface-subtle"
            >
              Rekonsiliasi
            </Link>
          </>
        ),
      }}
      kpiSlot={<KPIGrid items={kpis} columns={4} />}
    >
      <div className="flex flex-wrap gap-2 border-b border-border-subtle pb-3">
        <Button
          size="sm"
          variant={activeTab === 'pks' ? 'primary' : 'outline'}
          onClick={() => setActiveTab('pks')}
        >
          Master Data PKS (FLOW-06)
        </Button>
        {canReadFarmers ? (
          <Button
            size="sm"
            variant={activeTab === 'petani' ? 'primary' : 'outline'}
            onClick={() => setActiveTab('petani')}
          >
            Master Petani & Kebun
          </Button>
        ) : null}
        <Button
          size="sm"
          variant={activeTab === 'armada' ? 'primary' : 'outline'}
          onClick={() => setActiveTab('armada')}
        >
          Armada & Supir
        </Button>
      </div>

      {activeTab === 'pks' ? (
        <MillMasterSection canWrite={canWriteMills} />
      ) : activeTab === 'petani' ? (
        <FarmerFarmSection user={user} canWrite={canWriteFarmers} />
      ) : (
        <FleetMasterSection canWrite={canWriteMills} />
      )}
    </DashboardTemplate>
  );
}
