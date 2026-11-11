import { Link } from '@tanstack/react-router';
import { useState } from 'react';
import { Button } from '@/components/atoms';
import { KPIGrid, type KPIItem } from '@/components/organisms';
import { DashboardTemplate } from '@/components/templates';
import { hasPermission, type AuthenticatedUser } from '@/lib/auth/permissions';
import { FarmerFarmSection } from '@/features/master-data/components/FarmerFarmSection';
import { FleetMasterSection } from '@/features/master-data/components/FleetMasterSection';
import { useFarmers, useFarms, useVehicles } from '@/features/master-data/api/masterDataApi';

export function KoperasiHomePage({ user }: { readonly user: AuthenticatedUser }) {
  const [activeTab, setActiveTab] = useState<'petani-kebun' | 'armada'>('petani-kebun');
  const farmersQuery = useFarmers();
  const farmsQuery = useFarms();
  const vehiclesQuery = useVehicles();

  const canWrite = hasPermission(user, 'farmers.write');

  const kpis: KPIItem[] = [
    {
      id: 'k-farmers',
      label: 'Petani Dalam Cakupan',
      value: String(farmersQuery.data?.meta.total_items ?? 0),
      hint: 'Sesuai cakupan koperasi Anda',
    },
    {
      id: 'k-farms',
      label: 'Kebun Terdata',
      value: String(farmsQuery.data?.meta.total_items ?? 0),
    },
    {
      id: 'k-vehicles',
      label: 'Armada Terdaftar',
      value: String(vehiclesQuery.data?.meta.total_items ?? 0),
    },
    {
      id: 'k-flow05',
      label: 'Status FLOW-05',
      value: 'AKTIF',
      tone: 'primary',
      hint: 'Validasi koordinat & non-aktif aman',
    },
  ];

  return (
    <DashboardTemplate
      user={user}
      header={{
        eyebrow: 'PORTAL KOPERASI | FLOW-05',
        title: 'Dashboard & Master Data Koperasi',
        description:
          'Kelola data petani swadaya, profil kebun (STDB dan koordinat), serta armada kendaraan dalam cakupan koperasi Anda.',
        actions: (
          <>
            <Link
              to="/app/koperasi/penerimaan"
              className="inline-flex min-h-[44px] items-center rounded-md bg-primary-default px-4 text-sm font-semibold text-primary-foreground hover:bg-brand-hover"
            >
              Catat Penerimaan TBS
            </Link>
            <Link
              to="/app/koperasi/surat-jalan"
              className="inline-flex min-h-[44px] items-center rounded-md border border-border-control bg-surface-default px-4 text-sm font-semibold text-ink-primary hover:bg-surface-subtle"
            >
              Kelola e-DO
            </Link>
          </>
        ),
      }}
      kpiSlot={<KPIGrid items={kpis} columns={4} />}
    >
      <div className="flex flex-wrap gap-2 border-b border-border-subtle pb-3">
        <Button
          size="sm"
          variant={activeTab === 'petani-kebun' ? 'primary' : 'outline'}
          onClick={() => setActiveTab('petani-kebun')}
        >
          Master Petani & Kebun (FLOW-05)
        </Button>
        <Button
          size="sm"
          variant={activeTab === 'armada' ? 'primary' : 'outline'}
          onClick={() => setActiveTab('armada')}
        >
          Armada Kendaraan & Supir
        </Button>
      </div>

      {activeTab === 'petani-kebun' ? (
        <FarmerFarmSection user={user} canWrite={canWrite} />
      ) : (
        <FleetMasterSection canWrite={canWrite} />
      )}
    </DashboardTemplate>
  );
}
