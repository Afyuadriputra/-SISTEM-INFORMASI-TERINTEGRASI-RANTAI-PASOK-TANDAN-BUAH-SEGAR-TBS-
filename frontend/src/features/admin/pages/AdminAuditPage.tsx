import { useState } from 'react';
import { Badge, Button, Input } from '@/components/atoms';
import { DateRangeFilter, FormField, PolicyNoticeBanner } from '@/components/molecules';
import { DataTable, type DataTableColumn, StateFeedbackCard } from '@/components/organisms';
import { DataManagementTemplate } from '@/components/templates';
import { type AuditEvent, useAuditEvents } from '@/features/admin/api/adminApi';
import type { AuthenticatedUser } from '@/lib/auth/permissions';
import { formatWibDateTime } from '@/lib/decimal/precision';

export function AdminAuditPage({ user }: { readonly user: AuthenticatedUser }) {
  const [moduleFilter, setModuleFilter] = useState('');
  const [requestIdFilter, setRequestIdFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [page, setPage] = useState(1);

  const validRange = !dateFrom || !dateTo || dateFrom <= dateTo;

  const auditQuery = useAuditEvents(
    validRange
      ? {
          module: moduleFilter.trim() || undefined,
          request_id: requestIdFilter.trim() || undefined,
          date_from: dateFrom || undefined,
          date_to: dateTo || undefined,
          page,
        }
      : { page },
  );

  const columns: DataTableColumn<AuditEvent>[] = [
    {
      key: 'occurred_at',
      header: 'Waktu (WIB)',
      render: (row) => (
        <span className="whitespace-nowrap font-mono text-xs text-ink-secondary">
          {formatWibDateTime(row.occurred_at)}
        </span>
      ),
    },
    {
      key: 'event',
      header: 'Aksi & Modul',
      render: (row) => (
        <div>
          <p className="font-mono text-xs font-bold text-ink-primary">{row.event_type}</p>
          <p className="text-xs text-ink-muted">
            {row.module} | {row.resource_type}
          </p>
        </div>
      ),
    },
    {
      key: 'request_id',
      header: 'Request ID (CCTV)',
      render: (row) => (
        <span className="inline-block rounded bg-surface-subtle px-2 py-0.5 font-mono text-xs text-ink-primary">
          {row.request_id}
        </span>
      ),
    },
    {
      key: 'reason',
      header: 'Ringkasan / Alasan Audit',
      render: (row) => (
        <p className="max-w-md text-xs text-ink-secondary">
          {row.reason ?? 'Tidak ada catatan tambahan'}
        </p>
      ),
    },
  ];

  const meta = auditQuery.data?.meta;

  return (
    <DataManagementTemplate
      user={user}
      header={{
        eyebrow: 'TATA KELOLA & KEPATUHAN',
        title: 'Audit Trail Append-Only & CCTV Digital',
        description:
          'Jejak seluruh tindakan kritis bisnis, autentikasi, persetujuan Direksi, dan perubahan konfigurasi RBAC. Tidak dapat dimodifikasi atau dihapus (immutable).',
        actions: <Badge tone="neutral">Read-Only | Append-Only</Badge>,
      }}
      noticeSlot={
        <PolicyNoticeBanner
          kind="info"
          title="Redaksi Data Sensitif Audit (BSD-DEC-020)"
          description="Kata sandi, token CSRF, nomor rekening lengkap, dan rahasia infrastruktur diredaksi otomatis sebelum ditampilkan ke antarmuka audit."
        />
      }
      filterSlot={
        <div className="rounded-xl border border-border-subtle bg-surface-default p-4 shadow-sm">
          <div className="grid gap-4 lg:grid-cols-3">
            <FormField id="audit-module" label="Filter Modul / Entitas">
              <Input
                id="audit-module"
                value={moduleFilter}
                onChange={(e) => {
                  setModuleFilter(e.target.value);
                  setPage(1);
                }}
                placeholder="contoh: user_accounts, pricing..."
              />
            </FormField>
            <FormField id="audit-req-id" label="Cari Request ID">
              <Input
                id="audit-req-id"
                value={requestIdFilter}
                onChange={(e) => {
                  setRequestIdFilter(e.target.value);
                  setPage(1);
                }}
                placeholder="req-..."
              />
            </FormField>
            <DateRangeFilter
              fromDate={dateFrom}
              toDate={dateTo}
              onFromChange={(v) => {
                setDateFrom(v);
                setPage(1);
              }}
              onToChange={(v) => {
                setDateTo(v);
                setPage(1);
              }}
            />
          </div>
        </div>
      }
    >
      {auditQuery.isError ? (
        <StateFeedbackCard
          variant="error"
          title="Gagal Memuat Audit Trail"
          error={auditQuery.error}
          onAction={() => void auditQuery.refetch()}
        />
      ) : (
        <div className="space-y-4">
          <DataTable
            caption="Daftar Kejadian Audit Trail Append-Only"
            columns={columns}
            rows={auditQuery.data?.data ?? []}
            getRowKey={(r) => r.id}
            isLoading={auditQuery.isLoading}
            emptyTitle="Belum Ada Kejadian Audit Cocok"
            emptyDescription="Coba longgarkan filter modul, Request ID, atau rentang tanggal."
          />
          {meta && meta.total_pages > 1 ? (
            <div className="flex items-center justify-between text-xs text-ink-secondary">
              <span>
                Halaman {meta.page} dari {meta.total_pages} ({meta.total_items} entri)
              </span>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  disabled={!meta.has_prev}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                >
                  Sebelumnya
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={!meta.has_next}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Berikutnya
                </Button>
              </div>
            </div>
          ) : null}
        </div>
      )}
    </DataManagementTemplate>
  );
}
