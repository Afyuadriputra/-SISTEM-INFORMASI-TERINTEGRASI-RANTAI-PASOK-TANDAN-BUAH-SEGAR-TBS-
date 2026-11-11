import { Link } from '@tanstack/react-router';
import Decimal from 'decimal.js';
import { useState } from 'react';
import { Badge } from '@/components/atoms';
import { DateRangeFilter, PolicyNoticeBanner, StatusIndicator } from '@/components/molecules';
import { KPIGrid, type KPIItem, StateFeedbackCard } from '@/components/organisms';
import { ExecutiveTemplate } from '@/components/templates';
import { useInvoices } from '@/features/finance/api/financeApi';
import { useContracts } from '@/features/logistics/api/logisticsApi';
import { useReconciliations } from '@/features/reconciliation/api/reconciliationApi';
import {
  useFinanceReport,
  useOverviewReport,
  useReconciliationReport,
  useSupplyReport,
} from '@/features/reports/api/reportsApi';
import { type AuthenticatedUser, hasPermission } from '@/lib/auth/permissions';
import { formatIdr, formatKg } from '@/lib/decimal/precision';

export function DireksiDashboardPage({ user }: { readonly user: AuthenticatedUser }) {
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  const validRange = !dateFrom || !dateTo || dateFrom <= dateTo;
  const activeFilter = validRange
    ? { date_from: dateFrom || undefined, date_to: dateTo || undefined }
    : undefined;

  const canReadFinance = hasPermission(user, 'reports.finance.read');
  const canReadContracts = hasPermission(user, 'contracts.read');

  const overviewQuery = useOverviewReport(activeFilter);
  const supplyQuery = useSupplyReport(activeFilter);
  const reconQuery = useReconciliationReport(activeFilter);
  const financeQuery = useFinanceReport(activeFilter, canReadFinance);
  const invoicesQuery = useInvoices(hasPermission(user, 'invoices.read'));
  const contractsQuery = useContracts(canReadContracts);
  const reconCasesQuery = useReconciliations(undefined, hasPermission(user, 'reconciliations.read'));

  const pendingInvoices = (invoicesQuery.data?.data ?? []).filter(
    (inv) =>
      inv.status === 'DRAFT' ||
      inv.status === 'PENDING_VERIFICATION' ||
      (inv.status === 'ISSUED' && inv.settlement_status === 'AWAITING_PAYMENT'),
  );
  const pendingContracts = (contractsQuery.data?.data ?? []).filter(
    (c) => c.status === 'DRAFT' || c.status === 'PENDING_APPROVAL',
  );
  const disputeCases = (reconCasesQuery.data?.data ?? []).filter(
    (r) => r.status === 'DISPUTE_HOLD',
  );
  const pendingApprovalCount =
    pendingInvoices.length + pendingContracts.length + disputeCases.length;

  const overview = overviewQuery.data?.data;
  const supply = supplyQuery.data?.data;
  const reconReport = reconQuery.data?.data;
  const financeReport = financeQuery.data?.data;

  const kpis: KPIItem[] = [
    {
      id: 'dir-weight',
      label: 'Total Penerimaan Kebun',
      value: overview ? formatKg(overview.total_received_weight_kg) : '-',
      hint: overview ? `${overview.total_receipts_count} transaksi kebun` : undefined,
    },
    {
      id: 'dir-active-do',
      label: 'Pengiriman e-DO Aktif',
      value: String(overview?.active_deliveries_count ?? 0),
      hint: 'Tidak termasuk e-DO dibatalkan',
    },
    {
      id: 'dir-recon',
      label: 'Rekonsiliasi Cocok / Sengketa',
      value: overview
        ? `${overview.matched_reconciliations_count} / ${overview.dispute_reconciliations_count}`
        : '-',
      tone: (overview?.dispute_reconciliations_count ?? 0) > 0 ? 'warning' : 'primary',
      hint: 'Cocok dibanding sengketa aktif',
    },
    {
      id: 'dir-pending',
      label: 'Antrean Persetujuan Direksi',
      value: String(pendingApprovalCount),
      tone: pendingApprovalCount > 0 ? 'warning' : 'primary',
      hint: 'Faktur, kontrak, & eskalasi sengketa',
    },
  ];

  const byMillRows = supply?.by_mill ?? [];
  const maxMillWeight = byMillRows.reduce(
    (max, item) => Decimal.max(max, new Decimal(item.total_mill_weight_kg || '0')),
    new Decimal(1),
  );

  return (
    <ExecutiveTemplate
      user={user}
      header={{
        eyebrow: 'PORTAL EKSEKUTIF | DIREKSI PERUMDA',
        title: 'Dashboard Eksekutif Direksi (Unit Agro Niaga)',
        description:
          'Angka Piutang (AR), Kas Masuk, Hutang Disetujui (AP), & Kontribusi Kotor Simulasi dipisahkan tegas (BR-PAY-008/009 & BR-MRG-005). Unit Listrik & Gas di luar cakupan sistem.',
        actions: (
          <>
            <Link
              to="/app/direksi/persetujuan"
              className="inline-flex min-h-[44px] items-center rounded-md bg-primary-default px-4 text-sm font-semibold text-primary-foreground hover:bg-brand-hover"
            >
              Pusat Persetujuan ({pendingApprovalCount})
            </Link>
            <Link
              to="/app/admin/audit"
              className="inline-flex min-h-[44px] items-center rounded-md border border-border-control bg-surface-default px-4 text-sm font-semibold text-ink-primary hover:bg-surface-subtle"
            >
              Audit Trail Append-Only
            </Link>
          </>
        ),
      }}
      filterSlot={
        <div className="rounded-xl border border-border-subtle bg-surface-default p-4 shadow-sm">
          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
            <div className="w-full max-w-lg">
              <DateRangeFilter
                fromDate={dateFrom}
                toDate={dateTo}
                onFromChange={setDateFrom}
                onToChange={setDateTo}
                fromLabel="Periode Awal"
                toLabel="Periode Akhir"
              />
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone="warning">Data Simulasi Aktif</Badge>
              {overview ? (
                <Badge tone="neutral">
                  Periode: {overview.period_from} s.d. {overview.period_to}
                </Badge>
              ) : null}
            </div>
          </div>
        </div>
      }
      noticeSlot={
        <PolicyNoticeBanner
          kind="simulation"
          title="Transparansi Angka Eksekutif & Batasan Kebijakan"
          description="Kontribusi kotor yang ditampilkan bersifat simulasi selisih pendapatan jual terhadap pembayaran langsung yang terverifikasi, BUKAN Laba Bersih akuntansi (belum mengurangi biaya angkutan, operasional unit, maupun pajak)."
        />
      }
      kpiSlot={<KPIGrid items={kpis} columns={4} />}
    >
      {overviewQuery.isError ? (
        <StateFeedbackCard
          variant="error"
          title="Gagal Memuat Ringkasan Eksekutif"
          error={overviewQuery.error}
          onAction={() => void overviewQuery.refetch()}
        />
      ) : null}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="rounded-xl border border-border-subtle bg-surface-default p-5 shadow-sm">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
              <h2 className="text-base font-bold text-ink-primary">
                Antrean Persetujuan Kewenangan Direksi
              </h2>
              <Link
                to="/app/direksi/persetujuan"
                className="text-xs font-semibold text-primary-default hover:underline"
              >
                Buka Antrean Lengkap -&gt;
              </Link>
            </div>
            {pendingApprovalCount === 0 ? (
              <p className="rounded-md bg-surface-subtle p-4 text-sm text-ink-secondary">
                Tidak ada transaksi yang menunggu otorisasi Direksi saat ini.
              </p>
            ) : (
              <div className="space-y-2.5">
                {pendingContracts.slice(0, 3).map((c) => {
                  const totalQuota = c.quota_periods.reduce(
                    (acc, qp) => acc.plus(new Decimal(qp.quota_limit_kg)),
                    new Decimal(0),
                  );
                  return (
                    <div
                      key={c.id}
                      className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-border-subtle bg-surface-subtle p-3"
                    >
                      <div>
                        <p className="font-mono text-xs font-semibold text-ink-primary">
                          {c.contract_number} | {c.business_model_code}
                        </p>
                        <p className="text-xs text-ink-secondary">
                          Kuota {formatKg(totalQuota)} | Harga{' '}
                          {c.agreed_price_per_kg ? `${formatIdr(c.agreed_price_per_kg)}/kg` : c.price_rule_type}
                        </p>
                      </div>
                      <StatusIndicator status={c.status} />
                    </div>
                  );
                })}
                {pendingInvoices.slice(0, 3).map((inv) => (
                  <div
                    key={inv.id}
                    className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-accent-default/35 bg-warning-bg p-3"
                  >
                    <div>
                      <p className="font-mono text-xs font-semibold text-ink-primary">
                        {inv.invoice_number} ({inv.invoice_type})
                      </p>
                      <p className="text-xs text-ink-secondary">
                        Nilai: {formatIdr(inv.total_amount)} | Kebijakan:{' '}
                        {inv.policy_classification}
                      </p>
                    </div>
                    <StatusIndicator status={inv.status} />
                  </div>
                ))}
                {disputeCases.slice(0, 2).map((rec) => (
                  <div
                    key={rec.id}
                    className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-danger-text/30 bg-danger-bg p-3"
                  >
                    <div>
                      <p className="font-mono text-xs font-semibold text-danger-text">
                        Sengketa Rekonsiliasi | Selisih {formatKg(rec.difference_weight_kg)} (
                        {rec.difference_percent}%)
                      </p>
                      <p className="text-xs text-ink-secondary">
                        Asal {formatKg(rec.origin_weight_kg)} vs PKS{' '}
                        {formatKg(rec.mill_weight_kg ?? '0')}
                      </p>
                    </div>
                    <StatusIndicator status={rec.status} />
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-xl border border-border-subtle bg-surface-default p-5 shadow-sm">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
              <div>
                <h2 className="text-base font-bold text-ink-primary">
                  Realisasi Tonase Kebun vs PKS (Visualisasi Terarah)
                </h2>
                <p className="text-xs text-ink-secondary">
                  Asal Kebun: {supply ? formatKg(supply.total_origin_kg) : '0 kg'} | Terima PKS:{' '}
                  {supply ? formatKg(supply.total_mill_received_kg) : '0 kg'} | Dikecualikan
                  (Dibatalkan): {supply?.excluded_cancelled_count ?? 0}
                </p>
              </div>
            </div>
            {byMillRows.length === 0 ? (
              <p className="text-sm text-ink-secondary">
                Belum ada pengiriman e-DO aktif pada rentang filter ini.
              </p>
            ) : (
              <div className="space-y-4">
                {byMillRows.map((row) => {
                  const pct = new Decimal(row.total_mill_weight_kg || '0')
                    .div(maxMillWeight)
                    .times(100)
                    .toNumber();
                  return (
                    <div key={row.mill_id} className="space-y-1.5">
                      <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                        <span className="font-semibold text-ink-primary">{row.mill_name}</span>
                        <span className="font-mono text-ink-secondary">
                          {row.delivery_count} pengiriman | {formatKg(row.total_mill_weight_kg)}
                        </span>
                      </div>
                      <div className="h-3 w-full overflow-hidden rounded-full bg-surface-subtle">
                        <div
                          className="h-full rounded-full bg-primary-default transition-all"
                          style={{ width: `${Math.max(4, Math.min(100, pct))}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {reconReport ? (
              <div className="mt-5 grid grid-cols-2 gap-2 border-t border-border-subtle pt-4 text-xs sm:grid-cols-3">
                <div className="rounded bg-surface-subtle p-2.5">
                  <span className="text-ink-muted">Menunggu Tiket PKS</span>
                  <p className="font-mono text-sm font-bold text-ink-primary">
                    {reconReport.waiting_ticket_count}
                  </p>
                </div>
                <div className="rounded bg-surface-subtle p-2.5">
                  <span className="text-ink-muted">Cocok + Selesai</span>
                  <p className="font-mono text-sm font-bold text-primary-default">
                    {reconReport.matched_count + reconReport.resolved_count}
                  </p>
                </div>
                <div className="rounded bg-surface-subtle p-2.5">
                  <span className="text-ink-muted">Anomali Selisih Negatif</span>
                  <p className="font-mono text-sm font-bold text-danger-text">
                    {reconReport.negative_difference_count}
                  </p>
                </div>
              </div>
            ) : null}
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-xl border border-border-subtle bg-surface-default p-5 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-ink-muted">
              Piutang PKS (AR) vs Kas Masuk Riil (BR-PAY-008)
            </p>
            <p className="mt-2 font-mono text-xl font-bold text-primary-default">
              Kas: {financeReport ? formatIdr(financeReport.ar_cash_collected_total) : '-'}
            </p>
            <p className="mt-1 font-mono text-sm text-ink-secondary">
              Tagihan AR: {financeReport ? formatIdr(financeReport.ar_billed_total) : '-'}
            </p>
            <p className="mt-2 text-xs text-ink-secondary">
              Tagihan yang masih berstatus piutang berjalan belum dihitung sebagai kas tunai.
            </p>
          </div>

          <div className="rounded-xl border border-border-subtle bg-surface-default p-5 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wide text-ink-muted">
              Hutang Disetujui vs Terbayar (BR-PAY-009)
            </p>
            <p className="mt-2 font-mono text-xl font-bold text-ink-primary">
              Petani: {financeReport ? formatIdr(financeReport.farmer_disbursed_verified_total) : '-'}
            </p>
            <p className="mt-1 font-mono text-xs text-ink-secondary">
              AP Belum Cair: {financeReport ? formatIdr(financeReport.ap_approved_unpaid_total) : '-'}{' '}
              | AP Terbayar: {financeReport ? formatIdr(financeReport.ap_verified_paid_total) : '-'}
            </p>
          </div>

          <div className="rounded-xl border border-accent-default/40 bg-warning-bg p-5 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-xs font-bold uppercase tracking-wide text-warning-text">
                Kontribusi Kotor (Simulasi) != Laba Bersih
              </p>
              <Badge tone="warning">Bukan Laba Bersih</Badge>
            </div>
            <p className="mt-2 font-mono text-2xl font-bold text-ink-primary">
              {financeReport?.gross_contribution_simulation != null
                ? formatIdr(financeReport.gross_contribution_simulation)
                : 'Belum Dihitung'}
            </p>
            <p className="mt-2 text-xs font-medium text-warning-text">
              {financeReport?.margin_label ??
                'Kontribusi Kotor Niaga (Data Simulasi - Bukan Laba Bersih)'}
            </p>
            <p className="mt-1 text-xs text-ink-secondary">
              Selisih bruto dari tagihan jual dikurangi pembayaran terverifikasi. Belum
              memperhitungkan biaya operasional, angkutan, dan pajak (BR-MRG-005/006).
            </p>
          </div>
        </div>
      </div>
    </ExecutiveTemplate>
  );
}
