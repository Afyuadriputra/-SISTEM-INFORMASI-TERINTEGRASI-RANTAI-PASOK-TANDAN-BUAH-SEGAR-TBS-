import { CheckCircle2, FileUp, Scale } from 'lucide-react';
import { useState } from 'react';
import { Badge, Button, Input, Select } from '@/components/atoms';
import {
  FormField,
  PolicyNoticeBanner,
  StatusIndicator,
  WeightInputGroup,
} from '@/components/molecules';
import { DataTable, FormSection, StateFeedbackCard } from '@/components/organisms';
import { TransactionTemplate } from '@/components/templates';
import { useDeliveryOrders } from '@/features/logistics/api/logisticsApi';
import {
  useCreateMillTicket,
  useMillTickets,
  useUploadEvidenceFile,
  useVerifyMillTicket,
  type MillWeighingTicket,
} from '@/features/reconciliation/api/reconciliationApi';
import { hasPermission, type AuthenticatedUser } from '@/lib/auth/permissions';
import { computeNettoPreview, formatKg, formatWibDateTime } from '@/lib/decimal/precision';
import { ApiError } from '@/lib/errors/errorCatalog';
import { useUiStore } from '@/lib/state/uiStore';

export function MillTicketsPage({ user }: { readonly user: AuthenticatedUser }) {
  const pushToast = useUiStore((s) => s.pushToast);
  const canCreate = hasPermission(user, 'mill_tickets.create');
  const canVerify = hasPermission(user, 'mill_tickets.verify');

  const dosQuery = useDeliveryOrders();
  const ticketsQuery = useMillTickets();
  const createTicket = useCreateMillTicket();
  const verifyTicket = useVerifyMillTicket();
  const uploadFile = useUploadEvidenceFile();

  const deliveryOrders = dosQuery.data?.data ?? [];
  const tickets = ticketsQuery.data?.data ?? [];

  const [selectedDoId, setSelectedDoId] = useState('');
  const [ticketNumber, setTicketNumber] = useState('');
  const [grossWeight, setGrossWeight] = useState('18400.000');
  const [tareWeight, setTareWeight] = useState('8400.000');
  const [proofFileId, setProofFileId] = useState<string | null>(null);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const eligibleDos = deliveryOrders.filter((d) =>
    ['READY', 'IN_TRANSIT', 'ARRIVED', 'RECEIVED'].includes(d.status),
  );
  const resolvedDoId = selectedDoId || eligibleDos[0]?.id || '';

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setActionError(null);
    try {
      const res = await uploadFile.mutateAsync({
        classification: 'MILL_TICKET_PROOF',
        file,
      });
      setProofFileId(res.data.id);
      setUploadedFileName(res.data.original_filename);
      pushToast({
        tone: 'info',
        title: `Bukti slip ${res.data.original_filename} terunggah.`,
        requestId: res.request_id,
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const handleSubmitTicket = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    if (!resolvedDoId || !ticketNumber.trim()) {
      setActionError('Pilih e-DO pengiriman dan masukkan nomor tiket timbang PKS.');
      return;
    }
    const preview = computeNettoPreview(grossWeight, tareWeight);
    if (!preview.valid) {
      setActionError(preview.errorMessage ?? 'Nilai Bruto dan Tara tidak valid.');
      return;
    }
    try {
      const res = await createTicket.mutateAsync({
        delivery_order_id: resolvedDoId,
        ticket_number: ticketNumber.trim(),
        gross_weight_kg: Number(grossWeight).toFixed(3),
        tare_weight_kg: Number(tareWeight).toFixed(3),
        weighed_at: new Date().toISOString(),
        proof_file_id: proofFileId,
        grading_items: [],
      });
      setTicketNumber('');
      setProofFileId(null);
      setUploadedFileName(null);
      pushToast({
        tone: 'success',
        title: `Tiket timbang ${res.data.ticket_number} tersimpan (${formatKg(res.data.net_weight_kg)}).`,
        requestId: res.request_id,
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const handleVerify = async (ticket: MillWeighingTicket) => {
    setActionError(null);
    try {
      const res = await verifyTicket.mutateAsync(ticket.id);
      pushToast({
        tone: 'success',
        title: `Tiket ${res.data.ticket_number} terverifikasi dan siap masuk Rekonsiliasi.`,
        requestId: res.request_id,
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  return (
    <TransactionTemplate
      user={user}
      header={{
        eyebrow: 'PORTAL PKS | TIKET TIMBANG & GRADING PABRIK',
        title: 'Pencatatan Tiket Jembatan Timbang PKS',
        description:
          'Pendekatan A baseline MVP: pencatatan manual terverifikasi tiket timbang pabrik (1 tiket aktif final per e-DO).',
      }}
      noticeSlot={
        <PolicyNoticeBanner
          kind="pending_sop"
          title="Baseline Satu Tiket Final per e-DO (AFD §41 #6 & PRD §13.3)"
          description="Sistem menggunakan Pendekatan A (input manual terverifikasi tanpa integrasi langsung API/hardware jembatan timbang). Pengiriman ganda untuk e-DO yang sama otomatis ditolak (409 MILL_DUPLICATE_TICKET)."
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
              stepNumber="WB-01"
              title="Catat Tiket Timbang PKS Baru (Idempotent)"
              description="Pastikan nomor tiket jembatan timbang unik untuk e-DO tujuan PKS ini."
            >
              <form onSubmit={(e) => void handleSubmitTicket(e)} className="space-y-4">
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <FormField id="wb-edo" label="Surat Jalan e-DO" required>
                    <Select
                      id="wb-edo"
                      value={resolvedDoId}
                      onChange={(e) => setSelectedDoId(e.target.value)}
                    >
                      {eligibleDos.map((d) => (
                        <option key={d.id} value={d.id}>
                          {d.delivery_order_number} ({d.status}, asal {formatKg(d.total_origin_weight_kg)})
                        </option>
                      ))}
                    </Select>
                  </FormField>

                  <FormField id="wb-num" label="Nomor Tiket Timbang PKS" required>
                    <Input
                      id="wb-num"
                      monospace
                      placeholder="WB-PKC-2026-9950"
                      value={ticketNumber}
                      onChange={(e) => setTicketNumber(e.target.value)}
                    />
                  </FormField>
                </div>

                <WeightInputGroup
                  grossValue={grossWeight}
                  tareValue={tareWeight}
                  onGrossChange={setGrossWeight}
                  onTareChange={setTareWeight}
                />

                <FormField
                  id="wb-proof"
                  label="Unggah Bukti Slip Timbang PKS (PDF / Gambar)"
                  helperText={uploadedFileName ? `Terunggah: ${uploadedFileName}` : 'Opsional saat draf'}
                >
                  <div className="flex flex-wrap items-center gap-3">
                    <label
                      htmlFor="wb-proof"
                      className="inline-flex min-h-[44px] cursor-pointer items-center gap-2 rounded-md border border-border-control bg-surface-default px-3.5 text-xs font-semibold text-ink-primary hover:bg-surface-subtle"
                    >
                      <FileUp aria-hidden="true" className="h-4 w-4 text-primary-default" />
                      <span>{uploadFile.isPending ? 'Mengunggah...' : 'Pilih Berkas Bukti'}</span>
                      <input
                        id="wb-proof"
                        type="file"
                        accept=".pdf,image/*"
                        className="sr-only"
                        onChange={(e) => void handleFileChange(e)}
                      />
                    </label>
                    {proofFileId ? <Badge tone="success">ID Bukti Tersimpan</Badge> : null}
                  </div>
                </FormField>

                <Button
                  type="submit"
                  isLoading={createTicket.isPending}
                  leadingIcon={<Scale aria-hidden="true" className="h-4 w-4" />}
                >
                  Simpan Tiket Timbang PKS
                </Button>
              </form>
            </FormSection>
          ) : null}
        </div>
      }
      secondarySlot={
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-ink-primary">Daftar Tiket Timbang PKS</h2>
          {ticketsQuery.isError ? (
            <StateFeedbackCard
              variant="error"
              error={ticketsQuery.error}
              onAction={() => void ticketsQuery.refetch()}
            />
          ) : (
            <DataTable<MillWeighingTicket>
              caption="Daftar Tiket Timbang PKS"
              rows={tickets}
              isLoading={ticketsQuery.isLoading}
              getRowKey={(t) => t.id}
              columns={[
                {
                  key: 'ticket',
                  header: 'Tiket & Revisi',
                  render: (t) => (
                    <div>
                      <p className="font-mono text-xs font-bold text-primary-default">
                        {t.ticket_number}
                      </p>
                      <p className="text-xs text-ink-secondary">
                        Rev #{t.revision_number} | {formatWibDateTime(t.weighed_at)}
                      </p>
                    </div>
                  ),
                },
                {
                  key: 'netto',
                  header: 'Netto PKS',
                  align: 'right',
                  render: (t) => <span className="font-mono font-bold">{formatKg(t.net_weight_kg)}</span>,
                },
                {
                  key: 'status',
                  header: 'Status',
                  render: (t) => (
                    <div className="space-y-1">
                      <StatusIndicator status={t.status} />
                      {!t.is_current ? <Badge tone="neutral">Revisi Lama</Badge> : null}
                    </div>
                  ),
                },
                {
                  key: 'action',
                  header: 'Verifikasi',
                  render: (t) =>
                    t.is_current &&
                    (t.status === 'DRAFT' || t.status === 'SUBMITTED') &&
                    canVerify ? (
                      <Button
                        size="sm"
                        variant="primary"
                        isLoading={verifyTicket.isPending}
                        leadingIcon={<CheckCircle2 aria-hidden="true" className="h-3.5 w-3.5" />}
                        onClick={() => void handleVerify(t)}
                      >
                        Verifikasi Final
                      </Button>
                    ) : (
                      <span className="text-xs text-text-muted">-</span>
                    ),
                },
              ]}
            />
          )}
        </div>
      }
    />
  );
}
