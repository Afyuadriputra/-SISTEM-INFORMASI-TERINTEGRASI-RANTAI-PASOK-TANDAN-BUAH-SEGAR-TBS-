import { Link } from '@tanstack/react-router';
import { Badge } from '@/components/atoms';
import { PolicyNoticeBanner } from '@/components/molecules';
import { KPIGrid, type KPIItem, StateFeedbackCard } from '@/components/organisms';
import { DashboardTemplate } from '@/components/templates';
import {
  useAdminUsers,
  useAuditEvents,
  useSystemHealthSummary,
  useSystemRuleVersions,
} from '@/features/admin/api/adminApi';
import type { AuthenticatedUser } from '@/lib/auth/permissions';
import { formatWibDateTime } from '@/lib/decimal/precision';

export function AdminDashboardPage({ user }: { readonly user: AuthenticatedUser }) {
  const healthQuery = useSystemHealthSummary();
  const usersQuery = useAdminUsers();
  const rulesQuery = useSystemRuleVersions();
  const auditQuery = useAuditEvents({ page: 1 });

  const health = healthQuery.data?.data;
  const usersCount = usersQuery.data?.meta.total_items ?? 0;
  const rulesCount = rulesQuery.data?.meta.total_items ?? 0;

  const pgStatus = health?.health.dependencies?.postgresql ?? 'up';
  const redisStatus = health?.health.dependencies?.redis ?? 'up';

  const kpis: KPIItem[] = [
    {
      id: 'adm-pg',
      label: 'API & PostgreSQL (/health/ready)',
      value: health ? (pgStatus === 'up' ? 'SEHAT (UP)' : 'DEGRADED') : '-',
      tone: pgStatus === 'up' ? 'primary' : 'danger',
      hint: health ? `Status inti: ${health.health.status}` : 'Memeriksa kesiapan...',
    },
    {
      id: 'adm-redis',
      label: 'Redis Cache & Hit Ratio',
      value: health ? `${health.redis_cache_hit_ratio_percent}% (${redisStatus.toUpperCase()})` : '-',
      tone: redisStatus === 'up' ? 'primary' : 'danger',
      hint: 'Fallback DB langsung aktif bila Redis terganggu',
    },
    {
      id: 'adm-5xx',
      label: 'Insiden Error 5xx (24 Jam)',
      value: `${health?.server_errors_5xx_24h ?? 0} Insiden`,
      tone: (health?.server_errors_5xx_24h ?? 0) > 0 ? 'warning' : 'primary',
      hint: `Dari ${health?.total_requests_24h ?? 0} permintaan terpantau`,
    },
    {
      id: 'adm-rbac',
      label: 'Akun & Versi Aturan',
      value: `${usersCount} Akun | ${rulesCount} Versi`,
      hint: 'Pemisahan wewenang Non-Approver aktif',
    },
  ];

  const correlations = health?.recent_error_correlations ?? [];
  const latestAudits = (auditQuery.data?.data ?? []).slice(0, 5);

  return (
    <DashboardTemplate
      user={user}
      header={{
        eyebrow: 'ADMINISTRASI TI & OBSERVABILITAS',
        title: 'Dashboard Administrasi Teknis & Kesehatan Sistem',
        description:
          'Pemantauan teknis non-transaksional (CCTV Digital, Request ID, Redis & PostgreSQL health, serta status RBAC). Tidak menampilkan nominal transaksi maupun tombol persetujuan.',
        actions: (
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone="danger">Non-Approver (BR-SYS-002)</Badge>
            <Link
              to="/app/admin/pengguna"
              className="inline-flex min-h-[44px] items-center rounded-md bg-primary-default px-4 text-sm font-semibold text-primary-foreground hover:bg-brand-hover"
            >
              Pengguna & Versi Aturan
            </Link>
          </div>
        ),
      }}
      noticeSlot={
        <PolicyNoticeBanner
          kind="non_approver"
          title="Pemisahan Wewenang Administrator (BR-SYS-002)"
          description="Akun Administrator Sistem bersifat non-transaksional. Akses ke modul pembuatan faktur, verifikasi pembayaran, pengesahan kontrak, dan laporan margin keuangan diblokir di tingkat API dan UI."
        />
      }
      kpiSlot={<KPIGrid items={kpis} columns={4} />}
    >
      {healthQuery.isError ? (
        <StateFeedbackCard
          variant="error"
          title="Gagal Memuat Ringkasan Kesehatan Sistem"
          error={healthQuery.error}
          onAction={() => void healthQuery.refetch()}
        />
      ) : null}

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="rounded-xl border border-border-subtle bg-surface-default p-5 shadow-sm">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
              <h2 className="text-base font-bold text-ink-primary">
                Korelasi Error 5xx & CCTV Digital (Request ID / Trace ID)
              </h2>
              <Badge tone="neutral">{correlations.length} kejadian 24j</Badge>
            </div>
            {correlations.length === 0 ? (
              <p className="rounded-md bg-surface-subtle p-4 text-sm text-ink-secondary">
                Tidak ada insiden server 5xx tercatat dalam 24 jam terakhir.
              </p>
            ) : (
              <div className="space-y-2.5">
                {correlations.map((err) => (
                  <div
                    key={`${err.request_id}-${err.occurred_at}`}
                    className="rounded-md border border-danger-text/30 bg-danger-bg p-3 text-xs"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <span className="font-mono font-bold text-danger-text">
                        HTTP {err.status_code} | {err.error_code} | {err.module}
                      </span>
                      <span className="text-ink-muted">{formatWibDateTime(err.occurred_at)}</span>
                    </div>
                    <p className="mt-1 font-mono text-ink-primary">
                      Route: {err.route} | Request ID: {err.request_id} | Trace: {err.trace_id}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-xl border border-border-subtle bg-surface-default p-5 shadow-sm">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
              <h2 className="text-base font-bold text-ink-primary">
                Kejadian Audit & Keamanan Terbaru (Teredaksi)
              </h2>
              <Link
                to="/app/admin/audit"
                className="text-xs font-semibold text-primary-default hover:underline"
              >
                Buka Audit Trail Lengkap -&gt;
              </Link>
            </div>
            {latestAudits.length === 0 ? (
              <p className="text-sm text-ink-secondary">Belum ada aktivitas audit tercatat.</p>
            ) : (
              <div className="space-y-2">
                {latestAudits.map((ev) => (
                  <div
                    key={ev.id}
                    className="rounded-md border border-border-subtle bg-surface-subtle p-3 text-xs"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <span className="font-semibold text-ink-primary">
                        {ev.event_type} ({ev.module})
                      </span>
                      <span className="font-mono text-ink-muted">{ev.request_id}</span>
                    </div>
                    <p className="mt-1 text-ink-secondary">{ev.reason ?? 'Tanpa catatan tambahan'}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="h-fit rounded-xl border border-border-subtle bg-surface-default p-5 shadow-sm">
          <h2 className="mb-3 text-base font-bold text-ink-primary">Navigasi Modul Administrasi</h2>
          <div className="space-y-3">
            <Link
              to="/app/admin/pengguna"
              className="flex min-h-[44px] w-full items-center justify-between rounded-md bg-primary-default px-4 text-sm font-semibold text-primary-foreground hover:bg-brand-hover"
            >
              <span>Manajemen Pengguna & RBAC</span>
              <span aria-hidden="true">-&gt;</span>
            </Link>
            <Link
              to="/app/admin/audit"
              className="flex min-h-[44px] w-full items-center justify-between rounded-md border border-border-control bg-surface-default px-4 text-sm font-semibold text-ink-primary hover:bg-surface-subtle"
            >
              <span>Buka CCTV Digital & Audit Log</span>
              <span aria-hidden="true">-&gt;</span>
            </Link>
            <p className="pt-2 text-xs text-ink-secondary">
              Seluruh perubahan peran, pencabutan sesi, dan penambahan aturan sistem berversi dicatat
              otomatis sebagai entitas append-only tanpa penghapusan histori transaksi.
            </p>
          </div>
        </div>
      </div>
    </DashboardTemplate>
  );
}
