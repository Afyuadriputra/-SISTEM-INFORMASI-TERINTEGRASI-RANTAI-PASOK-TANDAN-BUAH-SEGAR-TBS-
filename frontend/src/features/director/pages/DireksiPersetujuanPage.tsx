import { CheckCircle2, FileText, Scale, ShieldCheck } from 'lucide-react';
import { useState } from 'react';
import { Badge, Button } from '@/components/atoms';
import { PolicyNoticeBanner, StatusIndicator } from '@/components/molecules';
import { ConfirmDialog, FormSection, KPIGrid, StateFeedbackCard, type KPIItem } from '@/components/organisms';
import { ExecutiveTemplate } from '@/components/templates';
import { useApproveContract, useContracts, type TradeContract } from '@/features/logistics/api/logisticsApi';
import { useReconciliations, useResolveDispute, type ReconciliationCase } from '@/features/reconciliation/api/reconciliationApi';
import type { AuthenticatedUser } from '@/lib/auth/permissions';
import { formatCalendarOrWibDate, formatIdr, formatKg } from '@/lib/decimal/precision';
import { ApiError } from '@/lib/errors/errorCatalog';
import { useUiStore } from '@/lib/state/uiStore';
import { useApproveOrRejectPayment, useInvoices, type Invoice } from '@/features/finance/api/financeApi';

export function DireksiPersetujuanPage({ user }: { readonly user: AuthenticatedUser }) {
  const pushToast = useUiStore((s) => s.pushToast);

  const invoicesQuery = useInvoices();
  const recsQuery = useReconciliations();
  const contractsQuery = useContracts();

  const approvePayment = useApproveOrRejectPayment();
  const resolveDispute = useResolveDispute();
  const approveContract = useApproveContract();

  const [actionError, setActionError] = useState<string | null>(null);
  const [dialogTarget, setDialogTarget] = useState<
    | { kind: 'payment_approve' | 'payment_reject'; item: Invoice }
    | { kind: 'dispute_resolve'; item: ReconciliationCase }
    | null
  >(null);

  const pendingPayments = (invoicesQuery.data?.data ?? []).filter(
    (inv) =>
      inv.invoice_type === 'ACCOUNTS_PAYABLE' &&
      inv.status === 'ISSUED' &&
      !inv.approvals.some((a) => a.decision === 'APPROVED'),
  );
  const pendingDisputes = (recsQuery.data?.data ?? []).filter((r) =>
    ['DISPUTE_HOLD', 'UNDER_REVIEW'].includes(r.status),
  );
  const pendingContracts = (contractsQuery.data?.data ?? []).filter(
    (c) => c.status === 'PENDING_APPROVAL',
  );

  const kpis: KPIItem[] = [
    {
      id: 'dir-pay',
      label: 'Otorisasi Pembayaran Pending',
      value: String(pendingPayments.length),
      tone: 'warning',
    },
    {
      id: 'dir-disp',
      label: 'Sengketa Berat Menunggu Putusan',
      value: String(pendingDisputes.length),
      tone: 'danger',
    },
    {
      id: 'dir-ctr',
      label: 'Kontrak Menunggu Persetujuan',
      value: String(pendingContracts.length),
      tone: 'primary',
    },
    {
      id: 'dir-sod',
      label: 'Proteksi Maker != Checker',
      value: 'AKTIF',
      hint: 'Pembuat faktur ditolak bila approve sendiri',
    },
  ];

  const handleConfirmDialog = async (reason: string) => {
    if (!dialogTarget) return;
    setActionError(null);
    try {
      if (dialogTarget.kind === 'payment_approve' || dialogTarget.kind === 'payment_reject') {
        const dec = dialogTarget.kind === 'payment_approve' ? 'APPROVED' : 'REJECTED';
        const invItem = dialogTarget.item;
        await approvePayment.mutateAsync({
          invoiceId: invItem.id,
          payload: { decision: dec, reason },
        });
        pushToast({
          tone: dec === 'APPROVED' ? 'success' : 'warning',
          title: `Otorisasi pembayaran ${invItem.invoice_number}: ${dec}.`,
        });
      } else if (dialogTarget.kind === 'dispute_resolve') {
        const recItem = dialogTarget.item;
        await resolveDispute.mutateAsync({
          reconciliationId: recItem.id,
          payload: {
            decision: 'ACCEPT_MILL_WEIGHT',
            final_outcome: 'RESOLVED',
            agreed_settlement_weight_kg: recItem.mill_weight_kg ?? recItem.origin_weight_kg,
            reason,
            evidence_file_id: null,
          },
        });
        pushToast({
          tone: 'success',
          title: `Sengketa ${recItem.delivery_order_number} diselesaikan (RESOLVED).`,
        });
      }
      setDialogTarget(null);
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
      setDialogTarget(null);
    }
  };

  const handleApproveContract = async (contract: TradeContract) => {
    setActionError(null);
    try {
      await approveContract.mutateAsync(contract.id);
      pushToast({
        tone: 'success',
        title: `Kontrak ${contract.contract_number} disetujui menjadi ACTIVE.`,
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  return (
    <>
      <ExecutiveTemplate
        user={user}
        header={{
          eyebrow: 'PORTAL DIREKSI | PUSAT PERSETUJUAN',
          title: 'Pusat Persetujuan Pembayaran, Sengketa & Kontrak',
          description:
            'Kelola seluruh keputusan otorisasi strategis Direksi Perumda dengan pemisahan tugas (Maker != Checker) serta catatan alasan audit.',
        }}
        noticeSlot={
          <PolicyNoticeBanner
            kind="pending_sop"
            title="Matriks Kewenangan & Batas Nilai Persetujuan (DEC-013 & AFD §41 #7, #8)"
            description="Persetujuan pembayaran hanya mengotorisasi pencairan (bukan tanda pelunasan PAID). Administrator Sistem dilarang keras mengakses fungsi ini (BR-SYS-002)."
          />
        }
        kpiSlot={<KPIGrid items={kpis} columns={4} />}
      >
        {actionError ? (
          <div
            role="alert"
            className="rounded-md border border-danger-text/30 bg-danger-bg px-4 py-3 text-sm font-medium text-danger-text"
          >
            {actionError}
          </div>
        ) : null}

        <div className="space-y-6">
          <FormSection
            stepNumber="01"
            title="Antrean Persetujuan Pembayaran (AP -> Koperasi)"
            description="Faktur terbit yang memerlukan otorisasi Direksi sebelum pencatatan transfer."
          >
            {invoicesQuery.isLoading ? (
              <StateFeedbackCard variant="loading" />
            ) : pendingPayments.length === 0 ? (
              <p className="text-sm text-text-muted">
                Tidak ada faktur AP yang menunggu persetujuan Direksi saat ini.
              </p>
            ) : (
              <div className="space-y-3">
                {pendingPayments.map((inv) => (
                  <div
                    key={inv.id}
                    className="flex flex-col justify-between gap-3 rounded-lg border border-border-subtle bg-surface-subtle/40 p-4 sm:flex-row sm:items-center"
                  >
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-sm font-bold text-primary-default">
                          {inv.invoice_number}
                        </span>
                        <Badge tone="warning">{inv.policy_classification}</Badge>
                      </div>
                      <p className="mt-1 font-mono text-base font-bold text-ink-primary">
                        {formatIdr(inv.total_amount)}
                      </p>
                      <p className="text-xs text-text-muted">
                        Jatuh tempo: {formatCalendarOrWibDate(inv.due_date)}
                      </p>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      <Button
                        size="sm"
                        variant="primary"
                        leadingIcon={<ShieldCheck aria-hidden="true" className="h-4 w-4" />}
                        onClick={() => setDialogTarget({ kind: 'payment_approve', item: inv })}
                      >
                        Setujui Pencairan
                      </Button>
                      <Button
                        size="sm"
                        variant="danger"
                        onClick={() => setDialogTarget({ kind: 'payment_reject', item: inv })}
                      >
                        Tolak
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </FormSection>

          <FormSection
            stepNumber="02"
            title="Antrean Penyelesaian Sengketa Selisih Berat"
            description="Kasus DISPUTE_HOLD / UNDER_REVIEW termasuk anomali selisih negatif."
          >
            {pendingDisputes.length === 0 ? (
              <p className="text-sm text-text-muted">Tidak ada sengketa menunggu putusan.</p>
            ) : (
              <div className="space-y-3">
                {pendingDisputes.map((rec) => (
                  <div
                    key={rec.id}
                    className="flex flex-col justify-between gap-3 rounded-lg border border-border-subtle bg-surface-subtle/40 p-4 sm:flex-row sm:items-center"
                  >
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="font-mono text-sm font-bold text-primary-default">
                          {rec.delivery_order_number}
                        </span>
                        <StatusIndicator status={rec.status} />
                        {rec.is_negative_difference ? (
                          <StatusIndicator status="ANOMALY_NEGATIVE_DIFFERENCE" />
                        ) : null}
                      </div>
                      <p className="mt-1 text-xs text-ink-secondary">
                        Asal: {formatKg(rec.origin_weight_kg)} vs PKS: {formatKg(rec.mill_weight_kg)}
                      </p>
                    </div>
                    <Button
                      size="sm"
                      variant="primary"
                      leadingIcon={<Scale aria-hidden="true" className="h-4 w-4" />}
                      onClick={() => setDialogTarget({ kind: 'dispute_resolve', item: rec })}
                    >
                      Putuskan Sengketa
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </FormSection>

          <FormSection
            stepNumber="03"
            title="Antrean Persetujuan Kontrak PKS"
            description="Aktifkan kontrak draf atau PENDING_APPROVAL."
          >
            {pendingContracts.length === 0 ? (
              <p className="text-sm text-text-muted">Tidak ada kontrak menunggu persetujuan.</p>
            ) : (
              <div className="space-y-3">
                {pendingContracts.map((ctr) => (
                  <div
                    key={ctr.id}
                    className="flex flex-col justify-between gap-3 rounded-lg border border-border-subtle bg-surface-subtle/40 p-4 sm:flex-row sm:items-center"
                  >
                    <div>
                      <div className="flex flex-wrap items-center gap-2">
                        <FileText aria-hidden="true" className="h-4 w-4 text-primary-default" />
                        <span className="font-mono text-sm font-bold text-ink-primary">
                          {ctr.contract_number}
                        </span>
                        <StatusIndicator status={ctr.business_model_code} />
                      </div>
                      <p className="mt-1 text-xs text-ink-secondary">{ctr.mill_name}</p>
                    </div>
                    <Button
                      size="sm"
                      variant="secondary"
                      isLoading={approveContract.isPending}
                      leadingIcon={<CheckCircle2 aria-hidden="true" className="h-4 w-4" />}
                      onClick={() => void handleApproveContract(ctr)}
                    >
                      Aktifkan Kontrak
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </FormSection>
        </div>
      </ExecutiveTemplate>

      <ConfirmDialog
        open={Boolean(dialogTarget)}
        title={
          dialogTarget?.kind === 'payment_approve'
            ? `Setujui Pembayaran ${dialogTarget.item.invoice_number}?`
            : dialogTarget?.kind === 'payment_reject'
              ? `Tolak Pembayaran ${dialogTarget.item.invoice_number}?`
              : dialogTarget?.kind === 'dispute_resolve'
                ? `Selesaikan Sengketa ${dialogTarget.item.delivery_order_number}?`
                : 'Konfirmasi Keputusan'
        }
        description="Keputusan ini akan disimpan pada jejak audit permanen Direksi."
        requireReason
        confirmLabel="Sahkan Keputusan"
        tone={dialogTarget?.kind === 'payment_reject' ? 'danger' : 'primary'}
        isSubmitting={approvePayment.isPending || resolveDispute.isPending}
        onConfirm={handleConfirmDialog}
        onCancel={() => setDialogTarget(null)}
      />
    </>
  );
}
