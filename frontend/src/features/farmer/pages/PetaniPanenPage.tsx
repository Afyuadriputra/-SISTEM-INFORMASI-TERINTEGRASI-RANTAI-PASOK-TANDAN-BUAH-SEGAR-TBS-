import { Link } from '@tanstack/react-router';
import { ArrowLeft } from 'lucide-react';
import { Badge } from '@/components/atoms';
import { PolicyNoticeBanner, StatusIndicator } from '@/components/molecules';
import { DataTable, StateFeedbackCard } from '@/components/organisms';
import { DashboardTemplate } from '@/components/templates';
import { usePayments, type PaymentRecord } from '@/features/finance/api/financeApi';
import { useReceipts, type TbsReceipt } from '@/features/receiving/api/receivingApi';
import type { AuthenticatedUser } from '@/lib/auth/permissions';
import { formatCalendarOrWibDate, formatIdr, formatKg, formatPercent, formatWibDateTime } from '@/lib/decimal/precision';

export function PetaniPanenPage({ user }: { readonly user: AuthenticatedUser }) {
  const receiptsQuery = useReceipts();
  const paymentsQuery = usePayments();

  const receipts = receiptsQuery.data?.data ?? [];
  const payments = paymentsQuery.data?.data ?? [];

  return (
    <DashboardTemplate
      user={user}
      header={{
        eyebrow: 'PORTAL PETANI | RIWAYAT PANEN & STATUS BAYAR',
        title: 'Riwayat Penimbangan Panen & Pembayaran Anda',
        description:
          'Rincian berat bruto, tara, netto, potongan mutu simulasi terpisah, serta status pembayaran yang terverifikasi.',
        actions: (
          <Link
            to="/app/petani"
            className="inline-flex min-h-[44px] items-center gap-1.5 rounded-md border border-border-control bg-surface-default px-4 text-sm font-semibold text-ink-primary hover:bg-surface-subtle"
          >
            <ArrowLeft aria-hidden="true" className="h-4 w-4" />
            <span>Kembali ke Ringkasan Petani</span>
          </Link>
        ),
      }}
      noticeSlot={
        <PolicyNoticeBanner
          kind="simulation"
          title="Transparansi Pembagian Hasil & Potongan Mutu (AFD §41 #4 & FR-REC-010)"
          description="Potongan mutu dan perhitungan alokasi multi-petani mengikuti aturan simulasi sampai SOP resmi Perumda disahkan. Pembayaran hanya berstatus PAID setelah bukti diverifikasi penuh."
        />
      }
    >
      {receiptsQuery.isError ? (
        <StateFeedbackCard
          variant="error"
          error={receiptsQuery.error}
          onAction={() => void receiptsQuery.refetch()}
        />
      ) : (
        <DataTable<TbsReceipt>
          caption="Riwayat Penerimaan Panen Pribadi"
          rows={receipts}
          isLoading={receiptsQuery.isLoading}
          getRowKey={(r) => r.id}
          columns={[
            {
              key: 'rcp',
              header: 'Penerimaan & Kebun',
              render: (r) => (
                <div>
                  <p className="font-mono text-xs font-bold text-primary-default">
                    {r.receipt_number}
                  </p>
                  <p className="text-xs font-semibold text-ink-primary">{r.farm_name}</p>
                  <p className="text-[11px] text-text-muted">{formatWibDateTime(r.received_at)}</p>
                </div>
              ),
            },
            {
              key: 'weights',
              header: 'Bruto / Tara / Netto',
              align: 'right',
              render: (r) =>
                r.current_weighing ? (
                  <div className="text-xs">
                    <p className="font-mono font-bold text-primary-default">
                      Netto: {formatKg(r.current_weighing.net_weight_kg)}
                    </p>
                    <p className="text-text-muted">
                      Bruto {formatKg(r.current_weighing.gross_weight_kg)} | Tara{' '}
                      {formatKg(r.current_weighing.tare_weight_kg)}
                    </p>
                  </div>
                ) : (
                  '-'
                ),
            },
            {
              key: 'grading',
              header: 'Potongan Grading Terpisah',
              align: 'right',
              render: (r) =>
                r.grading_items.length > 0 ? (
                  <div className="text-xs">
                    <p className="font-mono font-semibold">
                      {formatPercent(r.grading_items[0].deduction_value)}
                    </p>
                    <Badge tone="warning">Simulasi</Badge>
                    <p className="mt-0.5 text-text-muted">
                      Pasca-grading: {formatKg(r.net_weight_after_grading_kg)}
                    </p>
                  </div>
                ) : (
                  <span className="text-xs text-text-muted">Belum digrading</span>
                ),
            },
            {
              key: 'status',
              header: 'Status Penerimaan',
              render: (r) => <StatusIndicator status={r.status} />,
            },
          ]}
        />
      )}

      <section className="space-y-3">
        <h2 className="text-lg font-bold text-ink-primary">Riwayat Pembayaran Terkait</h2>
        <DataTable<PaymentRecord>
          caption="Riwayat Pembayaran Petani"
          rows={payments}
          isLoading={paymentsQuery.isLoading}
          getRowKey={(p) => p.id}
          columns={[
            {
              key: 'num',
              header: 'Nomor Pembayaran',
              render: (p) => (
                <div>
                  <p className="font-mono text-xs font-bold">{p.payment_number}</p>
                  <p className="text-xs text-text-muted">{p.payment_method}</p>
                </div>
              ),
            },
            {
              key: 'date',
              header: 'Tanggal',
              render: (p) => <span className="text-xs">{formatCalendarOrWibDate(p.payment_date)}</span>,
            },
            {
              key: 'amt',
              header: 'Nominal',
              align: 'right',
              render: (p) => <span className="font-mono font-bold">{formatIdr(p.amount)}</span>,
            },
            {
              key: 'status',
              header: 'Status',
              render: (p) => <StatusIndicator status={p.status} />,
            },
          ]}
        />
      </section>
    </DashboardTemplate>
  );
}
