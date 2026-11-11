import { CheckCircle2, FileUp, Plus, Receipt, ShieldAlert } from 'lucide-react';
import { useState } from 'react';
import { Badge, Button, Input, Select } from '@/components/atoms';
import { FormField, PolicyNoticeBanner, StatusIndicator } from '@/components/molecules';
import { DataTable, FormSection, KPIGrid, StateFeedbackCard, type KPIItem } from '@/components/organisms';
import { DataManagementTemplate } from '@/components/templates';
import {
  useReconciliations,
  useUploadEvidenceFile,
} from '@/features/reconciliation/api/reconciliationApi';
import { hasPermission, type AuthenticatedUser } from '@/lib/auth/permissions';
import { formatCalendarOrWibDate, formatIdr } from '@/lib/decimal/precision';
import { ApiError } from '@/lib/errors/errorCatalog';
import { useUiStore } from '@/lib/state/uiStore';
import {
  useCreateInvoiceDraft,
  useInvoices,
  useIssueInvoice,
  useRecordPayment,
  useVerifyInvoice,
  useVerifyPayment,
  type Invoice,
} from '../api/financeApi';

export function PerumdaFinancePage({ user }: { readonly user: AuthenticatedUser }) {
  const pushToast = useUiStore((s) => s.pushToast);

  const canCreateInv = hasPermission(user, 'invoices.create');
  const canVerifyInv = hasPermission(user, 'invoices.verify') && !user.non_approver_admin;
  const canIssueInv = hasPermission(user, 'invoices.issue');
  const canRecordPay = hasPermission(user, 'payments.record');
  const canVerifyPay = hasPermission(user, 'payments.verify') && !user.non_approver_admin;

  const invoicesQuery = useInvoices();
  const recsQuery = useReconciliations();
  const createInvoice = useCreateInvoiceDraft();
  const verifyInvoice = useVerifyInvoice();
  const issueInvoice = useIssueInvoice();
  const recordPayment = useRecordPayment();
  const verifyPayment = useVerifyPayment();
  const uploadFile = useUploadEvidenceFile();

  const invoices = invoicesQuery.data?.data ?? [];
  const recs = recsQuery.data?.data ?? [];

  const [invRecId, setInvRecId] = useState('');
  const [invType, setInvType] = useState<'ACCOUNTS_RECEIVABLE' | 'ACCOUNTS_PAYABLE'>(
    'ACCOUNTS_RECEIVABLE',
  );
  const [invDate, setInvDate] = useState('2026-11-11');

  const [payInvoiceId, setPayInvoiceId] = useState('');
  const [payAmount, setPayAmount] = useState('');
  const [payMethod, setPayMethod] = useState<'BANK_TRANSFER_MANUAL' | 'CASH_RECEIPT' | 'OTHER_VERIFIED'>(
    'BANK_TRANSFER_MANUAL',
  );
  const [payRef, setPayRef] = useState('');
  const [proofFileId, setProofFileId] = useState('a0000000-0000-4000-8000-000000000903');
  const [actionError, setActionError] = useState<string | null>(null);

  const selectedInvoiceForPay =
    invoices.find((i) => i.id === payInvoiceId) ??
    invoices.find((i) => i.status === 'ISSUED' && i.settlement_status !== 'PAID') ??
    invoices[0] ??
    null;

  const arInvoices = invoices.filter((i) => i.invoice_type === 'ACCOUNTS_RECEIVABLE');
  const apInvoices = invoices.filter((i) => i.invoice_type === 'ACCOUNTS_PAYABLE');

  const kpis: KPIItem[] = [
    {
      id: 'fin-ar',
      label: 'Faktur Piutang (PKS -> Perumda)',
      value: String(arInvoices.length),
      hint: 'AR terpisah dari kewajiban ke Koperasi',
    },
    {
      id: 'fin-ap',
      label: 'Faktur Kewajiban (Perumda -> Koperasi)',
      value: String(apInvoices.length),
    },
    {
      id: 'fin-await',
      label: 'Disetujui Belum Dibayar (APPROVED != PAID)',
      value: String(invoices.filter((i) => i.settlement_status === 'AWAITING_PAYMENT').length),
      tone: 'warning',
    },
    {
      id: 'fin-paid',
      label: 'Lunas Terverifikasi (PAID)',
      value: String(invoices.filter((i) => i.settlement_status === 'PAID').length),
      tone: 'primary',
    },
  ];

  const handleCreateInvoice = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    const chosenRecId = invRecId || recs[0]?.id;
    if (!chosenRecId) {
      setActionError('Pilih kasus rekonsiliasi terlebih dahulu.');
      return;
    }
    try {
      const res = await createInvoice.mutateAsync({
        invoice_type: invType,
        creditor_party_id: '10000000-0000-4000-8000-000000000100',
        debtor_party_id:
          invType === 'ACCOUNTS_RECEIVABLE'
            ? '10000000-0000-4000-8000-000000000120'
            : '10000000-0000-4000-8000-000000000110',
        reconciliation_case_id: chosenRecId,
        invoice_date: invDate,
        due_date: '2026-11-25',
      });
      pushToast({
        tone: 'success',
        title: `Draf faktur ${res.data.invoice_number} dibuat (${res.data.policy_classification}).`,
        requestId: res.request_id,
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const handleProofUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const res = await uploadFile.mutateAsync({ classification: 'PAYMENT_PROOF', file });
      setProofFileId(res.data.id);
      pushToast({ tone: 'info', title: `Bukti transfer ${res.data.original_filename} terunggah.` });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const handleRecordPayment = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    if (!selectedInvoiceForPay || !payRef.trim()) {
      setActionError('Pilih faktur dan isi referensi bukti transfer/kwitansi.');
      return;
    }
    const amt = (payAmount || selectedInvoiceForPay.total_amount).trim();
    try {
      const res = await recordPayment.mutateAsync({
        invoice_id: selectedInvoiceForPay.id,
        payment_direction:
          selectedInvoiceForPay.invoice_type === 'ACCOUNTS_RECEIVABLE' ? 'INBOUND' : 'OUTBOUND',
        payer_party_id: selectedInvoiceForPay.debtor_party_id,
        payee_party_id: selectedInvoiceForPay.creditor_party_id,
        amount: Number(amt).toFixed(2),
        payment_date: invDate,
        payment_method: payMethod,
        payment_reference: payRef.trim(),
        proof_file_id: proofFileId,
      });
      setPayRef('');
      setPayAmount('');
      pushToast({
        tone: 'success',
        title: `Catatan pembayaran ${res.data.payment_number} menunggu verifikasi checker.`,
        requestId: res.request_id,
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const runInvoiceAction = async (fn: () => Promise<unknown>, okMsg: string) => {
    setActionError(null);
    try {
      await fn();
      pushToast({ tone: 'success', title: okMsg });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  return (
    <DataManagementTemplate
      user={user}
      header={{
        eyebrow: 'PORTAL KEUANGAN PERUMDA | FAKTUR & PEMBAYARAN',
        title: 'Manajemen Faktur & Pencatatan Pembayaran Manual Terverifikasi',
        description:
          'Tanpa transfer bank otomatis (PRD §3.3): kelola penagihan PKS->Perumda (AR) terpisah dari kewajiban Perumda->Koperasi (AP), persetujuan berjenjang, dan pelunasan penuh.',
      }}
      noticeSlot={
        <div className="space-y-4">
          <PolicyNoticeBanner
            kind="pending_sop"
            title="Pemisahan Status & Kebijakan Pending SOP (BR-PAY-006, BR-PAY-010, AFD §41 #8-#10)"
            description="Persetujuan pembayaran (APPROVED) TIDAK berarti lunas (PAID). Pembayaran sebagian ditolak pada baseline MVP (PAY_PARTIAL_NOT_SUPPORTED), dan faktur dengan model usaha UNCONFIRMED diblokir penerbitannya (FIN_POLICY_UNCONFIRMED)."
          />
          <KPIGrid items={kpis} columns={4} />
        </div>
      }
      formSlot={
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
          {canCreateInv ? (
            <FormSection
              stepNumber="INV-01"
              title="Buat Draf Faktur dari Kasus Rekonsiliasi"
              description="Kasus yang masih DISPUTE_HOLD ditolak otomatis (FIN_DISPUTE_HOLD_BLOCKED)."
            >
              <form onSubmit={(e) => void handleCreateInvoice(e)} className="space-y-3">
                <FormField id="inv-rec" label="Kasus Rekonsiliasi">
                  <Select
                    id="inv-rec"
                    value={invRecId || recs[0]?.id || ''}
                    onChange={(e) => setInvRecId(e.target.value)}
                  >
                    {recs.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.delivery_order_number} ({r.status})
                      </option>
                    ))}
                  </Select>
                </FormField>

                <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                  <FormField id="inv-type" label="Jalur Faktur (AR vs AP Terpisah)">
                    <Select
                      id="inv-type"
                      value={invType}
                      onChange={(e) =>
                        setInvType(e.target.value as 'ACCOUNTS_RECEIVABLE' | 'ACCOUNTS_PAYABLE')
                      }
                    >
                      <option value="ACCOUNTS_RECEIVABLE">AR: Piutang PKS ke Perumda</option>
                      <option value="ACCOUNTS_PAYABLE">AP: Kewajiban Perumda ke Koperasi</option>
                    </Select>
                  </FormField>
                  <FormField id="inv-date" label="Tanggal Faktur" required>
                    <Input
                      id="inv-date"
                      type="date"
                      value={invDate}
                      onChange={(e) => setInvDate(e.target.value)}
                    />
                  </FormField>
                </div>

                <Button
                  type="submit"
                  isLoading={createInvoice.isPending}
                  leadingIcon={<Plus aria-hidden="true" className="h-4 w-4" />}
                >
                  Buat Draf Faktur
                </Button>
              </form>
            </FormSection>
          ) : null}

          {canRecordPay ? (
            <FormSection
              stepNumber="PAY-01"
              title="Catat Bukti Pembayaran Penuh (Idempotent)"
              description="Wajib nominal penuh sesuai total tagihan dan melampirkan bukti referensi."
            >
              <form onSubmit={(e) => void handleRecordPayment(e)} className="space-y-3">
                <FormField id="pay-inv" label="Faktur Terbit">
                  <Select
                    id="pay-inv"
                    value={selectedInvoiceForPay?.id ?? ''}
                    onChange={(e) => setPayInvoiceId(e.target.value)}
                  >
                    {invoices.map((inv) => (
                      <option key={inv.id} value={inv.id}>
                        {inv.invoice_number} ({formatIdr(inv.total_amount)} | {inv.settlement_status})
                      </option>
                    ))}
                  </Select>
                </FormField>

                <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                  <FormField
                    id="pay-amt"
                    label="Nominal Bayar (IDR)"
                    helperText={
                      selectedInvoiceForPay
                        ? `Penuh: ${formatIdr(selectedInvoiceForPay.total_amount)}`
                        : undefined
                    }
                  >
                    <Input
                      id="pay-amt"
                      monospace
                      placeholder={selectedInvoiceForPay?.total_amount ?? '0.00'}
                      value={payAmount}
                      onChange={(e) => setPayAmount(e.target.value)}
                    />
                  </FormField>
                  <FormField id="pay-method" label="Metode">
                    <Select
                      id="pay-method"
                      value={payMethod}
                      onChange={(e) => setPayMethod(e.target.value as typeof payMethod)}
                    >
                      <option value="BANK_TRANSFER_MANUAL">Transfer Bank Manual</option>
                      <option value="CASH_RECEIPT">Kwitansi Tunai Resmi</option>
                      <option value="OTHER_VERIFIED">Bukti Sah Lainnya</option>
                    </Select>
                  </FormField>
                  <FormField id="pay-ref" label="Nomor Referensi" required>
                    <Input
                      id="pay-ref"
                      monospace
                      placeholder="REF-TRF-2026-09"
                      value={payRef}
                      onChange={(e) => setPayRef(e.target.value)}
                    />
                  </FormField>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                  <label
                    htmlFor="pay-proof"
                    className="inline-flex min-h-[44px] cursor-pointer items-center gap-2 rounded-md border border-border-control bg-surface-default px-3.5 text-xs font-semibold text-ink-primary hover:bg-surface-subtle"
                  >
                    <FileUp aria-hidden="true" className="h-4 w-4 text-primary-default" />
                    <span>Unggah Bukti Transfer</span>
                    <input
                      id="pay-proof"
                      type="file"
                      accept=".pdf,image/*"
                      className="sr-only"
                      onChange={(e) => void handleProofUpload(e)}
                    />
                  </label>
                  <Button
                    type="submit"
                    isLoading={recordPayment.isPending}
                    leadingIcon={<Receipt aria-hidden="true" className="h-4 w-4" />}
                  >
                    Catat Bukti Pembayaran
                  </Button>
                </div>
              </form>
            </FormSection>
          ) : null}
        </div>
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

      {invoicesQuery.isError ? (
        <StateFeedbackCard
          variant="error"
          error={invoicesQuery.error}
          onAction={() => void invoicesQuery.refetch()}
        />
      ) : (
        <DataTable<Invoice>
          caption="Daftar Faktur AR/AP & Status Pembayaran"
          rows={invoices}
          isLoading={invoicesQuery.isLoading}
          getRowKey={(inv) => inv.id}
          columns={[
            {
              key: 'inv',
              header: 'Nomor & Jalur',
              render: (inv) => (
                <div>
                  <p className="font-mono text-xs font-bold text-primary-default">
                    {inv.invoice_number}
                  </p>
                  <p className="text-xs font-semibold text-ink-primary">{inv.invoice_type}</p>
                  <p className="text-[11px] text-text-muted">
                    Tgl: {formatCalendarOrWibDate(inv.invoice_date)}
                  </p>
                </div>
              ),
            },
            {
              key: 'amount',
              header: 'Total Tagihan',
              align: 'right',
              render: (inv) => (
                <div>
                  <p className="font-mono font-bold text-ink-primary">
                    {formatIdr(inv.total_amount)}
                  </p>
                  <Badge tone="warning">{inv.policy_classification}</Badge>
                </div>
              ),
            },
            {
              key: 'status',
              header: 'Status Dokumen & Pelunasan',
              render: (inv) => (
                <div className="space-y-1">
                  <StatusIndicator status={inv.status} />
                  <div>
                    <StatusIndicator status={inv.settlement_status} />
                  </div>
                </div>
              ),
            },
            {
              key: 'actions',
              header: 'Aksi Keuangan',
              render: (inv) => (
                <div className="flex flex-wrap gap-2">
                  {inv.status === 'DRAFT' && canVerifyInv ? (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() =>
                        void runInvoiceAction(
                          () =>
                            verifyInvoice.mutateAsync({
                              invoiceId: inv.id,
                              payload: { decision: 'APPROVE', reason: 'Terverifikasi keuangan' },
                            }),
                          `Faktur ${inv.invoice_number} diverifikasi.`,
                        )
                      }
                    >
                      Verifikasi
                    </Button>
                  ) : null}

                  {(inv.status === 'VERIFIED' || inv.status === 'DRAFT') && canIssueInv ? (
                    <Button
                      size="sm"
                      variant="primary"
                      leadingIcon={<ShieldAlert aria-hidden="true" className="h-3.5 w-3.5" />}
                      onClick={() =>
                        void runInvoiceAction(
                          () => issueInvoice.mutateAsync(inv.id),
                          `Faktur ${inv.invoice_number} diterbitkan.`,
                        )
                      }
                    >
                      Terbitkan Faktur
                    </Button>
                  ) : null}

                  {inv.payments
                    .filter((p) => p.status === 'PENDING_VERIFICATION')
                    .map((p) =>
                      canVerifyPay ? (
                        <Button
                          key={p.id}
                          size="sm"
                          variant="secondary"
                          leadingIcon={<CheckCircle2 aria-hidden="true" className="h-3.5 w-3.5" />}
                          onClick={() =>
                            void runInvoiceAction(
                              () =>
                                verifyPayment.mutateAsync({
                                  paymentId: p.id,
                                  payload: {
                                    decision: 'VERIFIED',
                                    reason: 'Bukti transfer cocok mutasi',
                                  },
                                }),
                              `Pelunasan ${p.payment_number} terverifikasi PAID.`,
                            )
                          }
                        >
                          Verifikasi Bayar ({p.payment_number})
                        </Button>
                      ) : null,
                    )}
                </div>
              ),
            },
          ]}
        />
      )}
    </DataManagementTemplate>
  );
}
