import { AlertTriangle, Calculator, Plus, Scale, ShieldAlert } from 'lucide-react';
import { useState } from 'react';
import { Badge, Button, Select } from '@/components/atoms';
import { FormField, PolicyNoticeBanner, StatusIndicator } from '@/components/molecules';
import {
  ConfirmDialog,
  DataTable,
  FilterPanel,
  FormSection,
  StateFeedbackCard,
} from '@/components/organisms';
import { DataManagementTemplate } from '@/components/templates';
import { useDeliveryOrders } from '@/features/logistics/api/logisticsApi';
import {
  useCalculateReconciliation,
  useComputeAllocations,
  useReconciliations,
  useResolveDispute,
  useSubmitDisputeReview,
  useTriggerReconciliation,
  type ReconciliationCase,
} from '@/features/reconciliation/api/reconciliationApi';
import { hasPermission, type AuthenticatedUser } from '@/lib/auth/permissions';
import { formatIdr, formatKg, formatPercent } from '@/lib/decimal/precision';
import { ApiError } from '@/lib/errors/errorCatalog';
import { useUiStore } from '@/lib/state/uiStore';

const SIM_ALLOCATION_POLICY_ID = '90000000-0000-4000-8000-000000000003';

export function PerumdaReconciliationPage({ user }: { readonly user: AuthenticatedUser }) {
  const pushToast = useUiStore((s) => s.pushToast);

  const canCalculate = hasPermission(user, 'reconciliations.calculate');
  const canReview = hasPermission(user, 'reconciliations.review');
  const canResolve = hasPermission(user, 'reconciliations.resolve') && !user.non_approver_admin;
  const canAllocate = hasPermission(user, 'allocations.compute');

  const [statusFilter, setStatusFilter] = useState('');
  const [triggerDoId, setTriggerDoId] = useState('');
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [dialogMode, setDialogMode] = useState<'review' | 'resolve' | null>(null);

  const canReadDos = hasPermission(user, 'delivery_orders.read');
  const dosQuery = useDeliveryOrders(undefined, canReadDos);
  const casesQuery = useReconciliations(statusFilter);
  const triggerRec = useTriggerReconciliation();
  const calcRec = useCalculateReconciliation();
  const reviewDispute = useSubmitDisputeReview();
  const resolveDispute = useResolveDispute();
  const computeAlloc = useComputeAllocations();

  const cases = casesQuery.data?.data ?? [];
  const deliveryOrders = dosQuery.data?.data ?? [];
  const reconcilableDos = deliveryOrders.filter(
    (d) =>
      ['RECEIVED', 'COMPLETED'].includes(d.status) &&
      !cases.some((c) => c.delivery_order_id === d.id),
  );
  const resolvedTriggerDoId =
    reconcilableDos.some((d) => d.id === triggerDoId)
      ? triggerDoId
      : (reconcilableDos[0]?.id ?? '');
  const activeCase = cases.find((c) => c.id === selectedId) ?? cases[0] ?? null;

  const handleTrigger = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resolvedTriggerDoId) {
      return;
    }
    setActionError(null);
    try {
      const res = await triggerRec.mutateAsync({
        delivery_order_id: resolvedTriggerDoId,
        weight_basis: 'NET_WEIGHT_BEFORE_GRADING',
      });
      setSelectedId(res.data.id);
      pushToast({
        tone: res.data.status === 'DISPUTE_HOLD' ? 'warning' : 'success',
        title: `Rekonsiliasi ${res.data.delivery_order_number} dihitung: ${res.data.status}.`,
        requestId: res.request_id,
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const handleCalculate = async (c: ReconciliationCase) => {
    setActionError(null);
    try {
      const res = await calcRec.mutateAsync(c.id);
      pushToast({
        tone: res.data.status === 'DISPUTE_HOLD' ? 'warning' : 'success',
        title: `Rekonsiliasi ${res.data.delivery_order_number} dihitung: ${res.data.status}.`,
        requestId: res.request_id,
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const handleAllocations = async (mode: 'SIMULATION' | 'FINAL') => {
    if (!activeCase) return;
    setActionError(null);
    try {
      const res = await computeAlloc.mutateAsync({
        reconciliationId: activeCase.id,
        payload: {
          mode,
          allocation_policy_version_id: SIM_ALLOCATION_POLICY_ID,
        },
      });
      pushToast({
        tone: 'info',
        title: `Simulasi pembagian ${res.data.length} lini petani dihitung (Label: SIMULATION_ONLY).`,
        requestId: res.request_id,
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const handleConfirmDispute = async (reason: string) => {
    if (!activeCase || !dialogMode) return;
    setActionError(null);
    try {
      if (dialogMode === 'review') {
        await reviewDispute.mutateAsync({
          reconciliationId: activeCase.id,
          payload: {
            decision: 'HOLD_FOR_AUDIT',
            reason,
            evidence_file_id: null,
            proposed_settlement_weight_kg: activeCase.mill_weight_kg ?? activeCase.origin_weight_kg,
          },
        });
        pushToast({ tone: 'info', title: 'Hasil pemeriksaan sengketa dicatat.' });
      } else {
        await resolveDispute.mutateAsync({
          reconciliationId: activeCase.id,
          payload: {
            decision: 'ACCEPT_MILL_WEIGHT',
            final_outcome: 'RESOLVED',
            agreed_settlement_weight_kg: activeCase.mill_weight_kg ?? activeCase.origin_weight_kg,
            reason,
            evidence_file_id: null,
          },
        });
        pushToast({ tone: 'success', title: `Sengketa ${activeCase.delivery_order_number} diselesaikan (RESOLVED).` });
      }
      setDialogMode(null);
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
      setDialogMode(null);
    }
  };

  return (
    <DataManagementTemplate
      user={user}
      header={{
        eyebrow: 'PORTAL PERUMDA | REKONSILIASI & SENGKETA BERAT',
        title: 'Rekonsiliasi Selisih Berat Koperasi vs PKS',
        description:
          'Bandingkan berat asal koperasi dan tiket timbang PKS pada dasar perhitungan setara, tangani sengketa susut serta anomali selisih negatif.',
      }}
      noticeSlot={
        <PolicyNoticeBanner
          kind="simulation"
          title="Aturan Simulasi Toleransi & Alokasi (BSD §11.3 & AFD §41 #2, #4)"
          description="Batas toleransi 1,5000% dan metode alokasi multi-petani menggunakan aturan simulasi sementara sebelum SOP resmi disahkan. Selisih negatif (berat PKS melebihi berat asal) otomatis ditahan untuk pemeriksaan (DISPUTE_HOLD)."
        />
      }
      filterSlot={
        <FilterPanel onReset={() => setStatusFilter('')}>
          <div className="min-w-[220px]">
            <label htmlFor="rec-status" className="mb-1 block text-xs font-semibold text-ink-secondary">
              Filter Status Rekonsiliasi
            </label>
            <Select id="rec-status" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">Semua Status</option>
              <option value="WAITING_TICKET">WAITING_TICKET</option>
              <option value="READY">READY</option>
              <option value="MATCHED">MATCHED</option>
              <option value="DISPUTE_HOLD">DISPUTE_HOLD</option>
              <option value="UNDER_REVIEW">UNDER_REVIEW</option>
              <option value="RESOLVED">RESOLVED</option>
            </Select>
          </div>
        </FilterPanel>
      }
      formSlot={
        canCalculate && reconcilableDos.length > 0 ? (
          <FormSection
            stepNumber="REC-01"
            title="Mulai & Hitung Rekonsiliasi e-DO Diterima PKS"
            description="Pilih pengiriman berstatus RECEIVED/COMPLETED yang tiket timbang PKS-nya sudah terverifikasi."
          >
            <form onSubmit={(e) => void handleTrigger(e)} className="flex flex-col gap-3 sm:flex-row sm:items-end">
              <div className="min-w-0 flex-1">
                <FormField id="rec-trigger-do" label="Surat Jalan e-DO Siap Rekonsiliasi" required>
                  <Select
                    id="rec-trigger-do"
                    value={resolvedTriggerDoId}
                    onChange={(e) => setTriggerDoId(e.target.value)}
                  >
                    {reconcilableDos.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.delivery_order_number} (Asal: {formatKg(d.total_origin_weight_kg)})
                      </option>
                    ))}
                  </Select>
                </FormField>
              </div>
              <Button
                type="submit"
                isLoading={triggerRec.isPending}
                leadingIcon={<Plus aria-hidden="true" className="h-4 w-4" />}
              >
                Buat & Hitung Rekonsiliasi
              </Button>
            </form>
          </FormSection>
        ) : undefined
      }
    >
      {actionError ? (
        <div
          role="alert"
          className="rounded-md border border-danger-text/30 bg-danger-bg px-4 py-3 text-sm font-medium text-danger-text"
        >
          {actionError}
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-12">
        <div className="min-w-0 xl:col-span-7">
          {casesQuery.isError ? (
            <StateFeedbackCard
              variant="error"
              error={casesQuery.error}
              onAction={() => void casesQuery.refetch()}
            />
          ) : (
            <DataTable<ReconciliationCase>
              caption="Daftar Kasus Rekonsiliasi Berat"
              rows={cases}
              isLoading={casesQuery.isLoading}
              getRowKey={(c) => c.id}
              columns={[
                {
                  key: 'edo',
                  header: 'e-DO & Revisi',
                  render: (c) => (
                    <button
                      type="button"
                      onClick={() => setSelectedId(c.id)}
                      className="text-left hover:underline"
                    >
                      <p className="font-mono text-xs font-bold text-primary-default">
                        {c.delivery_order_number}
                      </p>
                      <p className="text-xs text-text-muted">Rev #{c.revision_number}</p>
                    </button>
                  ),
                },
                {
                  key: 'weights',
                  header: 'Asal vs PKS',
                  align: 'right',
                  render: (c) => (
                    <div className="text-xs">
                      <p>Asal: {formatKg(c.origin_weight_kg)}</p>
                      <p>PKS: {formatKg(c.mill_weight_kg)}</p>
                    </div>
                  ),
                },
                {
                  key: 'diff',
                  header: 'Selisih / Toleransi',
                  align: 'right',
                  render: (c) => (
                    <div className="text-xs">
                      <p className="font-mono font-bold">
                        {formatKg(c.difference_weight_kg)} ({formatPercent(c.difference_percent)})
                      </p>
                      <p className="text-text-muted">Tol: {formatPercent(c.tolerance_percent)}</p>
                    </div>
                  ),
                },
                {
                  key: 'status',
                  header: 'Status & Anomali',
                  render: (c) => (
                    <div className="space-y-1">
                      <StatusIndicator status={c.status} />
                      {c.is_negative_difference ? (
                        <div>
                          <StatusIndicator status="ANOMALY_NEGATIVE_DIFFERENCE" />
                        </div>
                      ) : null}
                    </div>
                  ),
                },
              ]}
            />
          )}
        </div>

        <div className="min-w-0 xl:col-span-5">
          {activeCase ? (
            <FormSection
              stepNumber="REC"
              title={`Detail Kasus: ${activeCase.delivery_order_number}`}
              description={`Aturan Toleransi: ${formatPercent(activeCase.tolerance_percent)} (${activeCase.tolerance_policy_classification})`}
              aside={<StatusIndicator status={activeCase.status} />}
            >
              {activeCase.is_negative_difference ? (
                <div
                  role="alert"
                  className="flex items-start gap-2.5 rounded-md border border-danger-text/35 bg-danger-bg px-3.5 py-2.5 text-xs text-danger-text"
                >
                  <AlertTriangle aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0" />
                  <span>
                    Anomali Selisih Negatif terdeteksi: berat timbang PKS melebihi berat asal
                    koperasi (BR-REC-009). Wajib klarifikasi dan tidak dianggap susut wajar.
                  </span>
                </div>
              ) : null}

              <div className="grid grid-cols-2 gap-3 rounded-md border border-border-subtle bg-surface-subtle/60 p-3 text-xs">
                <div>
                  <p className="text-text-muted">Berat Asal Koperasi</p>
                  <p className="font-mono font-bold text-ink-primary">
                    {formatKg(activeCase.origin_weight_kg)}
                  </p>
                </div>
                <div>
                  <p className="text-text-muted">Berat Timbang PKS</p>
                  <p className="font-mono font-bold text-ink-primary">
                    {formatKg(activeCase.mill_weight_kg)}
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                {canCalculate && activeCase.status === 'READY' ? (
                  <Button
                    size="sm"
                    variant="primary"
                    isLoading={calcRec.isPending}
                    leadingIcon={<Calculator aria-hidden="true" className="h-3.5 w-3.5" />}
                    onClick={() => void handleCalculate(activeCase)}
                  >
                    Hitung Rekonsiliasi
                  </Button>
                ) : null}

                {canReview && activeCase.status === 'DISPUTE_HOLD' ? (
                  <Button size="sm" variant="secondary" onClick={() => setDialogMode('review')}>
                    Catat Klarifikasi Sengketa
                  </Button>
                ) : null}

                {canResolve &&
                ['DISPUTE_HOLD', 'UNDER_REVIEW'].includes(activeCase.status) ? (
                  <Button
                    size="sm"
                    variant="primary"
                    leadingIcon={<Scale aria-hidden="true" className="h-3.5 w-3.5" />}
                    onClick={() => setDialogMode('resolve')}
                  >
                    Putuskan Sengketa (Resolve)
                  </Button>
                ) : null}
              </div>

              {activeCase.dispute_reviews.length > 0 ? (
                <div className="space-y-2 border-t border-border-subtle pt-3">
                  <p className="text-xs font-bold uppercase text-ink-secondary">
                    Riwayat Klarifikasi Sengketa
                  </p>
                  {activeCase.dispute_reviews.map((rev) => (
                    <div
                      key={rev.id}
                      className="rounded border border-border-subtle bg-surface-default px-3 py-2 text-xs"
                    >
                      <p className="font-semibold text-ink-primary">{rev.decision}</p>
                      <p className="mt-0.5 text-ink-secondary">{rev.reason}</p>
                    </div>
                  ))}
                </div>
              ) : null}

              <div className="space-y-3 border-t border-border-subtle pt-3">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="text-xs font-bold uppercase text-ink-secondary">
                    Simulasi Pembagian Hasil Multi-Petani (30/20/50)
                  </p>
                  <Badge tone="warning">Pending SOP (AFD §41 #4)</Badge>
                </div>

                {canAllocate ? (
                  <div className="flex flex-wrap gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      isLoading={computeAlloc.isPending}
                      onClick={() => void handleAllocations('SIMULATION')}
                    >
                      Jalankan Simulasi Alokasi
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      leadingIcon={<ShieldAlert aria-hidden="true" className="h-3.5 w-3.5" />}
                      onClick={() => void handleAllocations('FINAL')}
                    >
                      Uji Finalisasi Alokasi Resmi
                    </Button>
                  </div>
                ) : null}

                {activeCase.farmer_allocations.length > 0 ? (
                  <ul className="divide-y divide-border-subtle rounded border border-border-subtle text-xs">
                    {activeCase.farmer_allocations.map((al) => (
                      <li key={al.id} className="flex items-center justify-between px-3 py-2">
                        <div>
                          <p className="font-semibold text-ink-primary">{al.farmer_name}</p>
                          <p className="text-[11px] text-text-muted">
                            {formatKg(al.agreed_weight_kg)} | {al.policy_classification}
                          </p>
                        </div>
                        <span className="font-mono font-bold text-primary-default">
                          {formatIdr(al.net_amount)}
                        </span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-text-muted">
                    Belum ada simulasi alokasi yang dijalankan untuk kasus ini.
                  </p>
                )}
              </div>
            </FormSection>
          ) : null}
        </div>
      </div>

      <ConfirmDialog
        open={Boolean(dialogMode)}
        title={
          dialogMode === 'review'
            ? `Catat Pemeriksaan Sengketa ${activeCase?.delivery_order_number ?? ''}`
            : `Putuskan Penyelesaian Sengketa ${activeCase?.delivery_order_number ?? ''}`
        }
        description="Keputusan penyelesaian sengketa wajib mencantumkan alasan jelas serta menjadi dasar pembukaan blokir penagihan (AFD §20)."
        requireReason
        confirmLabel={dialogMode === 'review' ? 'Simpan Pemeriksaan' : 'Sahkan Penyelesaian'}
        isSubmitting={reviewDispute.isPending || resolveDispute.isPending}
        onConfirm={handleConfirmDispute}
        onCancel={() => setDialogMode(null)}
      />
    </DataManagementTemplate>
  );
}
