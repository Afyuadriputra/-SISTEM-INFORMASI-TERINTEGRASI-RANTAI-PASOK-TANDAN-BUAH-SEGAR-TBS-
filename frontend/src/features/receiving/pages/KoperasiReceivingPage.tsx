import { CheckCircle2, Lock, Plus, Scale, Trash2 } from 'lucide-react';
import { useState } from 'react';
import { Badge, Button, Input, Select } from '@/components/atoms';
import {
  FormField,
  PolicyNoticeBanner,
  StatusIndicator,
  WeightInputGroup,
} from '@/components/molecules';
import {
  ConfirmDialog,
  DataTable,
  FormSection,
  StateFeedbackCard,
} from '@/components/organisms';
import { TransactionTemplate } from '@/components/templates';
import { useFarmers, useFarms } from '@/features/master-data/api/masterDataApi';
import { hasPermission, type AuthenticatedUser } from '@/lib/auth/permissions';
import { computeNettoPreview, formatKg, formatPercent, formatWibDateTime } from '@/lib/decimal/precision';
import { ApiError } from '@/lib/errors/errorCatalog';
import { useUiStore } from '@/lib/state/uiStore';
import {
  useCancelReceipt,
  useCreateReceiptDraft,
  useReceipts,
  useRecordGrading,
  useRecordWeighing,
  useValidateReceipt,
  type TbsReceipt,
} from '../api/receivingApi';

export function KoperasiReceivingPage({ user }: { readonly user: AuthenticatedUser }) {
  const pushToast = useUiStore((s) => s.pushToast);

  const canCreate = hasPermission(user, 'receipts.create');
  const canWeigh = hasPermission(user, 'receipts.weigh');
  const canValidate = hasPermission(user, 'receipts.validate');
  const canCancel = hasPermission(user, 'receipts.cancel');

  const [selectedFarmerId, setSelectedFarmerId] = useState('');
  const [selectedFarmId, setSelectedFarmId] = useState('');
  const [harvestDate, setHarvestDate] = useState('2026-11-11');
  const [notes, setNotes] = useState('');

  const [activeReceiptId, setActiveReceiptId] = useState<string | null>(null);
  const [grossWeight, setGrossWeight] = useState('4200.000');
  const [tareWeight, setTareWeight] = useState('1200.000');
  const [correctionReason, setCorrectionReason] = useState('');
  const [gradingPercent, setGradingPercent] = useState('2.0000');
  const [gradingCategory, setGradingCategory] = useState('Sortasi Mutu Simulasi (Basah/Brondolan)');
  const [receiptToCancel, setReceiptToCancel] = useState<TbsReceipt | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const farmersQuery = useFarmers();
  const farmsQuery = useFarms();
  const receiptsQuery = useReceipts();

  const createDraft = useCreateReceiptDraft();
  const recordWeighing = useRecordWeighing();
  const recordGrading = useRecordGrading();
  const validateReceipt = useValidateReceipt();
  const cancelReceipt = useCancelReceipt();

  const farmers = farmersQuery.data?.data ?? [];
  const allFarms = farmsQuery.data?.data ?? [];
  const receipts = receiptsQuery.data?.data ?? [];

  const resolvedFarmerId = selectedFarmerId || farmers[0]?.id || '';
  const farmsForFarmer = allFarms.filter((f) => !resolvedFarmerId || f.farmer_id === resolvedFarmerId);
  const resolvedFarmId =
    farmsForFarmer.some((f) => f.id === selectedFarmId)
      ? selectedFarmId
      : (farmsForFarmer[0]?.id ?? '');

  const activeReceipt =
    receipts.find((r) => r.id === activeReceiptId) ?? receipts[0] ?? null;

  const isActiveLocked = activeReceipt
    ? ['ALLOCATED', 'SHIPPED', 'CLOSED', 'CANCELLED'].includes(activeReceipt.status)
    : false;

  const handleSelectReceipt = (r: TbsReceipt) => {
    setActiveReceiptId(r.id);
    setActionError(null);
    if (r.current_weighing) {
      setGrossWeight(r.current_weighing.gross_weight_kg);
      setTareWeight(r.current_weighing.tare_weight_kg);
    }
    setCorrectionReason('');
  };

  const handleCreateDraft = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    if (!resolvedFarmerId || !resolvedFarmId) {
      setActionError('Pilih petani dan kebun asal sebelum membuat draf penerimaan.');
      return;
    }
    try {
      const res = await createDraft.mutateAsync({
        payload: {
          farmer_id: resolvedFarmerId,
          farm_id: resolvedFarmId,
          harvest_date: harvestDate || null,
          received_at: new Date().toISOString(),
          notes: notes.trim() || null,
        },
        idempotencyScope: `receipt:draft:${resolvedFarmerId}:${resolvedFarmId}:${harvestDate}`,
      });
      setActiveReceiptId(res.data.id);
      setNotes('');
      pushToast({
        tone: 'success',
        title: `Penerimaan ${res.data.receipt_number} dibuat.`,
        requestId: res.request_id,
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const handleSaveWeighing = async () => {
    if (!activeReceipt) return;
    setActionError(null);
    const preview = computeNettoPreview(grossWeight, tareWeight);
    if (!preview.valid) {
      setActionError(preview.errorMessage ?? 'Nilai timbang belum valid.');
      return;
    }
    try {
      const res = await recordWeighing.mutateAsync({
        receiptId: activeReceipt.id,
        payload: {
          gross_weight_kg: Number(grossWeight).toFixed(3),
          tare_weight_kg: Number(tareWeight).toFixed(3),
          correction_reason:
            activeReceipt.status === 'VALIDATED' ? correctionReason.trim() : null,
          version: activeReceipt.version,
        },
      });
      pushToast({
        tone: 'success',
        title: `Timbangan ${res.data.receipt_number} tercatat (Netto: ${formatKg(res.data.current_weighing?.net_weight_kg)}).`,
        requestId: res.request_id,
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const handleSaveGrading = async () => {
    if (!activeReceipt) return;
    setActionError(null);
    const pct = Number(gradingPercent);
    if (!Number.isFinite(pct) || pct < 0 || pct > 100) {
      setActionError('Persentase potongan simulasi harus antara 0% sampai 100%.');
      return;
    }
    try {
      const res = await recordGrading.mutateAsync({
        receiptId: activeReceipt.id,
        payload: {
          items: [
            {
              grading_category: gradingCategory.trim() || 'Sortasi Mutu Simulasi',
              measurement_value: pct.toFixed(4),
              deduction_type: 'WEIGHT_PERCENT',
              deduction_value: pct.toFixed(4),
              calculation_basis: 'NET_WEIGHT_BEFORE_GRADING',
              notes: 'Potongan terpisah dari berat netto (BSD §9.3 Simulasi)',
            },
          ],
          version: activeReceipt.version,
        },
      });
      pushToast({
        tone: 'success',
        title: `Grading ${res.data.receipt_number} dicatat. Netto pasca-grading: ${formatKg(res.data.net_weight_after_grading_kg)}.`,
        requestId: res.request_id,
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const handleValidate = async () => {
    if (!activeReceipt) return;
    setActionError(null);
    try {
      const res = await validateReceipt.mutateAsync({
        receiptId: activeReceipt.id,
        version: activeReceipt.version,
      });
      pushToast({
        tone: 'success',
        title: `Penerimaan ${res.data.receipt_number} divalidasi dan siap dialokasikan ke e-DO.`,
        requestId: res.request_id,
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const handleConfirmCancel = async (reason: string) => {
    if (!receiptToCancel) return;
    setActionError(null);
    try {
      await cancelReceipt.mutateAsync({
        receiptId: receiptToCancel.id,
        reason,
        version: receiptToCancel.version,
      });
      pushToast({ tone: 'info', title: `Penerimaan ${receiptToCancel.receipt_number} dibatalkan.` });
      setReceiptToCancel(null);
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
      setReceiptToCancel(null);
    }
  };

  return (
    <>
      <TransactionTemplate
        user={user}
        header={{
        eyebrow: 'PORTAL KOPERASI | PENERIMAAN, TIMBANG & GRADING',
        title: 'Pencatatan Penerimaan & Penimbangan TBS',
        description:
          'Catat penerimaan panen petani, timbang Bruto dan Tara (Netto dihitung otoritatif server), serta catat potongan grading secara terpisah.',
      }}
      noticeSlot={
        <PolicyNoticeBanner
          kind="simulation"
          title="Aturan Simulasi Grading (BSD §9.3 & AFD §41 #3)"
          description="Potongan grading (contoh standar 2,0000%) berstatus aturan simulasi menunggu pengesahan SOP dan disimpan sebagai komponen terpisah dari berat netto (BR-TBS-005). Penerimaan yang sudah teralokasi ke e-DO aktif otomatis terkunci."
        />
      }
      primarySlot={
        <div className="space-y-6">
          {actionError ? (
            <div
              role="alert"
              className="rounded-md border border-danger-text/30 bg-danger-bg px-4 py-3 text-sm font-medium text-danger-text"
            >
              {actionError}
            </div>
          ) : null}

          {canCreate ? (
            <FormSection
              stepNumber="TBS-01"
              title="Buat Draf Penerimaan Baru (Idempotent)"
              description="Langkah pertama sebelum penimbangan. Setiap pengiriman ulang dilindungi Idempotency-Key."
            >
              <form onSubmit={(e) => void handleCreateDraft(e)} className="space-y-3">
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <FormField id="rcp-farmer" label="Petani Pemasok" required>
                    <Select
                      id="rcp-farmer"
                      value={resolvedFarmerId}
                      onChange={(e) => setSelectedFarmerId(e.target.value)}
                    >
                      {farmers.map((fm) => (
                        <option key={fm.id} value={fm.id}>
                          {fm.farmer_code} - {fm.full_name}
                        </option>
                      ))}
                    </Select>
                  </FormField>
                  <FormField id="rcp-farm" label="Kebun Asal TBS" required>
                    <Select
                      id="rcp-farm"
                      value={resolvedFarmId}
                      onChange={(e) => setSelectedFarmId(e.target.value)}
                    >
                      {farmsForFarmer.map((fb) => (
                        <option key={fb.id} value={fb.id}>
                          {fb.farm_code} - {fb.farm_name}
                        </option>
                      ))}
                    </Select>
                  </FormField>
                </div>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <FormField id="rcp-harvest" label="Tanggal Panen">
                    <Input
                      id="rcp-harvest"
                      type="date"
                      value={harvestDate}
                      onChange={(e) => setHarvestDate(e.target.value)}
                    />
                  </FormField>
                  <FormField id="rcp-notes" label="Catatan Penerimaan">
                    <Input
                      id="rcp-notes"
                      placeholder="Jumlah tandan atau kondisi buah"
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                    />
                  </FormField>
                </div>
                <Button
                  type="submit"
                  isLoading={createDraft.isPending}
                  leadingIcon={<Plus aria-hidden="true" className="h-4 w-4" />}
                >
                  Buat Draf Penerimaan
                </Button>
              </form>
            </FormSection>
          ) : null}

          {activeReceipt ? (
            <FormSection
              stepNumber="TBS-02"
              title={`Timbang & Grading: ${activeReceipt.receipt_number}`}
              description={`${activeReceipt.farmer_name} | ${activeReceipt.farm_name}`}
              aside={<StatusIndicator status={activeReceipt.status} />}
            >
              {isActiveLocked ? (
                <PolicyNoticeBanner
                  kind="non_approver"
                  title={`Terkunci (${activeReceipt.status})`}
                  description="Transaksi penerimaan ini telah dialokasikan ke e-DO aktif atau selesai/dibatalkan sehingga berat tidak dapat diubah (BR-012)."
                />
              ) : null}

              <WeightInputGroup
                grossValue={grossWeight}
                tareValue={tareWeight}
                onGrossChange={setGrossWeight}
                onTareChange={setTareWeight}
                disabled={isActiveLocked || !canWeigh}
              />

              {activeReceipt.status === 'VALIDATED' ? (
                <FormField
                  id="weigh-correction-reason"
                  label="Alasan Koreksi Timbang (Wajib setelah Validasi BR-011)"
                  required
                >
                  <Input
                    id="weigh-correction-reason"
                    placeholder="Jelaskan alasan revisi berat"
                    value={correctionReason}
                    onChange={(e) => setCorrectionReason(e.target.value)}
                  />
                </FormField>
              ) : null}

              {canWeigh ? (
                <div className="flex flex-wrap gap-2">
                  <Button
                    type="button"
                    variant="primary"
                    disabled={isActiveLocked}
                    isLoading={recordWeighing.isPending}
                    leadingIcon={<Scale aria-hidden="true" className="h-4 w-4" />}
                    onClick={() => void handleSaveWeighing()}
                  >
                    Simpan Penimbangan
                  </Button>
                </div>
              ) : null}

              <div className="border-t border-border-subtle pt-4">
                <div className="mb-2 flex items-center justify-between gap-2">
                  <p className="text-sm font-bold text-ink-primary">Sortasi Mutu / Grading</p>
                  <Badge tone="warning">Aturan Simulasi</Badge>
                </div>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                  <div className="sm:col-span-2">
                    <FormField id="grd-cat" label="Kategori Potongan Mutu">
                      <Input
                        id="grd-cat"
                        disabled={isActiveLocked || !canWeigh}
                        value={gradingCategory}
                        onChange={(e) => setGradingCategory(e.target.value)}
                      />
                    </FormField>
                  </div>
                  <FormField id="grd-pct" label="Potongan (%)">
                    <Input
                      id="grd-pct"
                      monospace
                      disabled={isActiveLocked || !canWeigh}
                      value={gradingPercent}
                      onChange={(e) => setGradingPercent(e.target.value)}
                    />
                  </FormField>
                </div>

                <div className="mt-3 flex flex-wrap gap-2">
                  {canWeigh ? (
                    <Button
                      type="button"
                      variant="secondary"
                      disabled={isActiveLocked || !activeReceipt.current_weighing}
                      isLoading={recordGrading.isPending}
                      onClick={() => void handleSaveGrading()}
                    >
                      Catat Grading Simulasi
                    </Button>
                  ) : null}

                  {canValidate && activeReceipt.status === 'DRAFT' ? (
                    <Button
                      type="button"
                      variant="primary"
                      disabled={!activeReceipt.current_weighing}
                      isLoading={validateReceipt.isPending}
                      leadingIcon={<CheckCircle2 aria-hidden="true" className="h-4 w-4" />}
                      onClick={() => void handleValidate()}
                    >
                      Validasi Penerimaan
                    </Button>
                  ) : null}

                  {canCancel && !isActiveLocked ? (
                    <Button
                      type="button"
                      variant="danger"
                      leadingIcon={<Trash2 aria-hidden="true" className="h-4 w-4" />}
                      onClick={() => setReceiptToCancel(activeReceipt)}
                    >
                      Batalkan
                    </Button>
                  ) : null}
                </div>
              </div>
            </FormSection>
          ) : null}
        </div>
      }
      secondarySlot={
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-ink-primary">Daftar Penerimaan TBS</h2>
          {receiptsQuery.isError ? (
            <StateFeedbackCard
              variant="error"
              error={receiptsQuery.error}
              onAction={() => void receiptsQuery.refetch()}
            />
          ) : (
            <DataTable<TbsReceipt>
              caption="Antrean Penerimaan TBS Koperasi"
              rows={receipts}
              isLoading={receiptsQuery.isLoading}
              getRowKey={(r) => r.id}
              columns={[
                {
                  key: 'num',
                  header: 'Nomor & Petani',
                  render: (r) => (
                    <button
                      type="button"
                      onClick={() => handleSelectReceipt(r)}
                      className="text-left hover:underline"
                    >
                      <p className="font-mono text-xs font-bold text-primary-default">
                        {r.receipt_number}
                      </p>
                      <p className="text-xs font-semibold text-ink-primary">{r.farmer_name}</p>
                      <p className="text-[11px] text-text-muted">
                        {formatWibDateTime(r.received_at)}
                      </p>
                    </button>
                  ),
                },
                {
                  key: 'weight',
                  header: 'Netto & Potongan',
                  align: 'right',
                  render: (r) => (
                    <div className="text-xs">
                      <p className="font-mono font-bold text-ink-primary">
                        {formatKg(r.current_weighing?.net_weight_kg)}
                      </p>
                      {r.grading_items.length > 0 ? (
                        <p className="text-text-muted">
                          Pot. {formatPercent(r.grading_items[0].deduction_value)} | Bersih:{' '}
                          {formatKg(r.net_weight_after_grading_kg)}
                        </p>
                      ) : null}
                    </div>
                  ),
                },
                {
                  key: 'status',
                  header: 'Status',
                  render: (r) => (
                    <div className="space-y-1">
                      <StatusIndicator status={r.status} />
                      {['ALLOCATED', 'SHIPPED', 'CLOSED'].includes(r.status) ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-ink-secondary">
                          <Lock aria-hidden="true" className="h-3 w-3" />
                          <span>Terkunci e-DO</span>
                        </span>
                      ) : null}
                    </div>
                  ),
                },
              ]}
            />
          )}
        </div>
      }
    />
      <ConfirmDialog
        open={Boolean(receiptToCancel)}
        title={`Batalkan Penerimaan ${receiptToCancel?.receipt_number ?? ''}?`}
        description="Pembatalan penerimaan hanya diizinkan sebelum alokasi ke e-DO aktif dan wajib mencatat alasan audit."
        requireReason
        confirmLabel="Batalkan Penerimaan"
        tone="danger"
        isSubmitting={cancelReceipt.isPending}
        onConfirm={handleConfirmCancel}
        onCancel={() => setReceiptToCancel(null)}
      />
    </>
  );
}
