import { Link } from '@tanstack/react-router';
import { Sprout } from 'lucide-react';
import { LocationLink, PolicyNoticeBanner, StatusIndicator } from '@/components/molecules';
import { DataTable, KPIGrid, StateFeedbackCard, type KPIItem } from '@/components/organisms';
import { DashboardTemplate } from '@/components/templates';
import { usePayments, type PaymentRecord } from '@/features/finance/api/financeApi';
import { useFarmers, useFarms, type Farm } from '@/features/master-data/api/masterDataApi';
import { useReceipts } from '@/features/receiving/api/receivingApi';
import type { AuthenticatedUser } from '@/lib/auth/permissions';
import { formatCalendarOrWibDate, formatHectares, formatIdr, formatKg } from '@/lib/decimal/precision';

export function PetaniDashboardPage({ user }: { readonly user: AuthenticatedUser }) {
  const farmersQuery = useFarmers();
  const farmsQuery = useFarms();
  const receiptsQuery = useReceipts();
  const paymentsQuery = usePayments();

  const farmer = farmersQuery.data?.data?.[0] ?? null;
  const farms = farmsQuery.data?.data ?? [];
  const receipts = receiptsQuery.data?.data ?? [];
  const payments = paymentsQuery.data?.data ?? [];

  const totalNetKg = receipts.reduce(
    (sum, r) => sum + Number(r.current_weighing?.net_weight_kg ?? 0),
    0,
  );
  const verifiedPaymentsCount = payments.filter((p) => p.status === 'VERIFIED').length;

  const kpis: KPIItem[] = [
    {
      id: 'ptn-farms',
      label: 'Kebun Terdaftar Milik Sendiri',
      value: String(farms.length),
      hint: farmer ? `Kode Petani: ${farmer.farmer_code}` : 'Cakupan pribadi',
    },
    {
      id: 'ptn-receipts',
      label: 'Total Penerimaan Panen Anda',
      value: String(receipts.length),
    },
    {
      id: 'ptn-kg',
      label: 'Akumulasi Netto Timbangan',
      value: formatKg(totalNetKg.toFixed(3)),
      tone: 'primary',
    },
    {
      id: 'ptn-pay',
      label: 'Pembayaran Terverifikasi',
      value: String(verifiedPaymentsCount),
      hint: 'Hanya status terverifikasi dihitung lunas',
    },
  ];

  return (
    <DashboardTemplate
      user={user}
      header={{
        eyebrow: 'PORTAL PETANI SWADAYA | HANYA BACA (BR-MD-004)',
        title: 'Portal Transparansi Petani',
        description:
          'Pantau profil kebun pribadi, catatan hasil timbang panen Anda, serta status pembayaran yang telah diverifikasi tanpa menampilkan data petani lain.',
        actions: (
          <Link
            to="/app/petani/panen"
            className="inline-flex min-h-[44px] items-center rounded-md bg-primary-default px-4 text-sm font-semibold text-primary-foreground hover:bg-brand-hover"
          >
            Lihat Rincian Panen & Pembayaran
          </Link>
        ),
      }}
      noticeSlot={
        <PolicyNoticeBanner
          kind="info"
          title="Isolasi Data Pribadi Petani & Mode Baca-Saja (BR-MD-004 & E2E-06)"
          description="Akun petani hanya dapat melihat profil, kebun, panen, dan status pembayaran milik sendiri secara baca-saja. Pelunasan tidak akan berstatus lunas sebelum bukti pembayaran diverifikasi."
        />
      }
      kpiSlot={<KPIGrid items={kpis} columns={4} />}
    >
      {farmer ? (
        <section className="rounded-lg border border-border-subtle bg-surface-default p-5">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <Sprout aria-hidden="true" className="h-5 w-5 text-primary-default" />
              <h2 className="text-base font-bold text-ink-primary">{farmer.full_name}</h2>
            </div>
            <StatusIndicator status={farmer.status} />
          </div>
          <p className="mt-1 font-mono text-xs text-text-muted">
            {farmer.farmer_code} | Anggota: {farmer.membership_number || '-'}
          </p>
        </section>
      ) : null}

      <section className="space-y-3">
        <h2 className="text-lg font-bold text-ink-primary">Daftar Kebun Pribadi Anda</h2>
        {farmsQuery.isError ? (
          <StateFeedbackCard
            variant="error"
            error={farmsQuery.error}
            onAction={() => void farmsQuery.refetch()}
          />
        ) : (
          <DataTable<Farm>
            caption="Daftar Kebun Milik Petani"
            rows={farms}
            isLoading={farmsQuery.isLoading}
            getRowKey={(f) => f.id}
            columns={[
              {
                key: 'code',
                header: 'Kebun',
                render: (f) => (
                  <div>
                    <p className="font-mono text-xs font-bold text-primary-default">{f.farm_code}</p>
                    <p className="font-semibold text-ink-primary">{f.farm_name}</p>
                    <p className="text-xs text-text-muted">STDB: {f.stdb_number || '-'}</p>
                  </div>
                ),
              },
              {
                key: 'area',
                header: 'Luas & Tahun Tanam',
                align: 'right',
                render: (f) => (
                  <div className="text-xs">
                    <p className="font-mono font-bold">{formatHectares(f.area_hectares)}</p>
                    <p className="text-text-muted">Tanam: {f.planting_year ?? '-'}</p>
                  </div>
                ),
              },
              {
                key: 'loc',
                header: 'Lokasi',
                render: (f) => (
                  <LocationLink
                    address={f.village || 'Desa terdaftar'}
                    district={f.district}
                    latitude={f.latitude}
                    longitude={f.longitude}
                    hasVerifiedCoordinates={Boolean(f.latitude && f.longitude)}
                  />
                ),
              },
            ]}
          />
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-bold text-ink-primary">Ringkasan Status Pembayaran</h2>
        <DataTable<PaymentRecord>
          caption="Status Pembayaran Terverifikasi"
          rows={payments}
          isLoading={paymentsQuery.isLoading}
          getRowKey={(p) => p.id}
          emptyTitle="Belum Ada Catatan Pembayaran"
          emptyDescription="Status pembayaran akan muncul setelah transaksi direkonsiliasi dan diverifikasi."
          columns={[
            {
              key: 'num',
              header: 'Referensi Pembayaran',
              render: (p) => (
                <div>
                  <p className="font-mono text-xs font-bold text-primary-default">
                    {p.payment_number}
                  </p>
                  <p className="text-xs text-text-muted">{p.payment_reference}</p>
                </div>
              ),
            },
            {
              key: 'date',
              header: 'Tanggal',
              render: (p) => <span className="text-xs">{formatCalendarOrWibDate(p.payment_date)}</span>,
            },
            {
              key: 'amount',
              header: 'Nilai',
              align: 'right',
              render: (p) => <span className="font-mono font-bold">{formatIdr(p.amount)}</span>,
            },
            {
              key: 'status',
              header: 'Status Verifikasi',
              render: (p) => <StatusIndicator status={p.status} />,
            },
          ]}
        />
      </section>
    </DashboardTemplate>
  );
}
