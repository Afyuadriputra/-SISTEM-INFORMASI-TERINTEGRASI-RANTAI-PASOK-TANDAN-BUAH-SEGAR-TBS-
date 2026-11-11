import { Check, Plus, Send, ShieldAlert, XCircle } from 'lucide-react';
import { useState } from 'react';
import { Badge, Button, Input, Select } from '@/components/atoms';
import {
  FormField,
  PolicyNoticeBanner,
  SearchField,
  StatusIndicator,
} from '@/components/molecules';
import {
  ConfirmDialog,
  DataTable,
  FilterPanel,
  FormSection,
  StateFeedbackCard,
} from '@/components/organisms';
import { DataManagementTemplate } from '@/components/templates';
import { useMills } from '@/features/master-data/api/masterDataApi';
import { usePublicDisbunPrices } from '@/features/public/api/publicApi';
import { hasPermission, type AuthenticatedUser } from '@/lib/auth/permissions';
import { formatPricePerKg, formatWibDateTime } from '@/lib/decimal/precision';
import { ApiError } from '@/lib/errors/errorCatalog';
import { useUiStore } from '@/lib/state/uiStore';
import {
  useCreateDisbunPrice,
  useCreatePriceDraft,
  useInternalPrices,
  usePricingMetadata,
  usePublishPrice,
  useRevokePrice,
  useSubmitPrice,
  useVerifyOrRejectPrice,
  type InternalPriceQuote,
} from '../api/pricingApi';

export function PerumdaPricingPage({ user }: { readonly user: AuthenticatedUser }) {
  const pushToast = useUiStore((s) => s.pushToast);

  const canCreate = hasPermission(user, 'prices.create');
  const canVerify = hasPermission(user, 'prices.verify') && !user.non_approver_admin;
  const canPublish = hasPermission(user, 'prices.publish');
  const canRevoke = hasPermission(user, 'prices.revoke');

  const [statusFilter, setStatusFilter] = useState('');
  const [search, setSearch] = useState('');
  const [actionError, setActionError] = useState<string | null>(null);

  const [millId, setMillId] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [sourceId, setSourceId] = useState('');
  const [pricePerKg, setPricePerKg] = useState('2850.00');
  const [effectiveFrom, setEffectiveFrom] = useState('2026-11-11T08:00');
  const [effectiveUntil, setEffectiveUntil] = useState('2026-11-18T17:00');
  const [notes, setNotes] = useState('');

  const [disbunPrice, setDisbunPrice] = useState('3120.00');
  const [disbunCategoryId, setDisbunCategoryId] = useState('');

  const [dialogAction, setDialogAction] = useState<{
    kind: 'reject' | 'revoke';
    quote: InternalPriceQuote;
  } | null>(null);

  const metaQuery = usePricingMetadata();
  const millsQuery = useMills();
  const pricesQuery = useInternalPrices({ status: statusFilter, search });
  const disbunQuery = usePublicDisbunPrices();

  const createDraft = useCreatePriceDraft();
  const submitPrice = useSubmitPrice();
  const verifyPrice = useVerifyOrRejectPrice();
  const publishPrice = usePublishPrice();
  const revokePrice = useRevokePrice();
  const createDisbun = useCreateDisbunPrice();

  const sources = metaQuery.data?.data.sources ?? [];
  const categories = metaQuery.data?.data.categories ?? [];
  const mills = millsQuery.data?.data ?? [];
  const quotes = pricesQuery.data?.data ?? [];
  const disbunList = disbunQuery.data?.data ?? [];

  const handleCreateDraft = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    const chosenMill = millId || mills[0]?.id;
    const chosenCat = categoryId || categories[0]?.id;
    const chosenSrc = sourceId || sources.find((s) => s.source_type !== 'DISBUN')?.id || sources[0]?.id;
    if (!chosenMill || !chosenCat || !chosenSrc) {
      setActionError('Pilih PKS, kategori kualitas, dan sumber harga terlebih dahulu.');
      return;
    }
    const parsedPrice = Number(pricePerKg);
    if (!Number.isFinite(parsedPrice) || parsedPrice <= 0) {
      setActionError('Harga TBS harus lebih besar dari Rp 0,00/kg.');
      return;
    }
    try {
      const res = await createDraft.mutateAsync({
        mill_id: chosenMill,
        price_category_id: chosenCat,
        source_id: chosenSrc,
        price_per_kg: parsedPrice.toFixed(2),
        effective_from: new Date(effectiveFrom).toISOString(),
        effective_until: effectiveUntil ? new Date(effectiveUntil).toISOString() : null,
        notes: notes.trim() || null,
      });
      pushToast({
        tone: 'success',
        title: `Draf harga ${res.data.mill_code} (${formatPricePerKg(res.data.price_per_kg)}) tersimpan.`,
        requestId: res.request_id,
      });
      setNotes('');
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const handleCreateDisbun = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    const disbunSrc = sources.find((s) => s.source_type === 'DISBUN') ?? sources[0];
    const chosenCat = disbunCategoryId || categories[0]?.id;
    const parsed = Number(disbunPrice);
    if (!disbunSrc || !chosenCat || !Number.isFinite(parsed) || parsed <= 0) {
      setActionError('Data acuan Disbun belum valid.');
      return;
    }
    try {
      const res = await createDisbun.mutateAsync({
        price_source_id: disbunSrc.id,
        price_category_id: chosenCat,
        price_per_kg: parsed.toFixed(2),
        effective_from: new Date().toISOString(),
        effective_until: new Date(Date.now() + 7 * 86400_000).toISOString(),
      });
      pushToast({
        tone: 'success',
        title: `Acuan Disbun ${formatPricePerKg(res.data.price_per_kg)} dicatat terpisah.`,
        requestId: res.request_id,
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const runSimpleTransition = async (fn: () => Promise<unknown>, successTitle: string) => {
    setActionError(null);
    try {
      await fn();
      pushToast({ tone: 'success', title: successTitle });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const handleConfirmDialog = async (reason: string) => {
    if (!dialogAction) return;
    setActionError(null);
    try {
      if (dialogAction.kind === 'reject') {
        await verifyPrice.mutateAsync({
          priceQuoteId: dialogAction.quote.id,
          payload: { decision: 'REJECT', reason },
        });
        pushToast({ tone: 'info', title: 'Kutipan harga ditolak dengan alasan tercatat.' });
      } else {
        await revokePrice.mutateAsync({
          priceQuoteId: dialogAction.quote.id,
          reason,
        });
        pushToast({ tone: 'warning', title: 'Kutipan harga publik telah dicabut.' });
      }
      setDialogAction(null);
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
      setDialogAction(null);
    }
  };

  return (
    <DataManagementTemplate
      user={user}
      header={{
        eyebrow: 'PORTAL PERUMDA | HARGA TBS MULTI-PKS',
        title: 'Manajemen Harga Multi-PKS & Acuan Disbun',
        description:
          'Alur empat mata: Penyusunan Draf -> Pengajuan Verifikasi -> Verifikasi Petugas Berbeda (Maker != Checker) -> Publikasi Terkurasi ke Portal Publik.',
      }}
      noticeSlot={
        <PolicyNoticeBanner
          kind="info"
          title="Pemisahan Tugas & Sumber Harga (BR-PRC-006 & BR-004)"
          description="Petugas yang mengajukan verifikasi harga tidak boleh memverifikasi kutipan yang sama (Maker != Checker). Harga acuan Dinas Perkebunan dikelola terpisah dari harga beli PKS mitra."
        />
      }
      filterSlot={
        <FilterPanel
          onReset={() => {
            setStatusFilter('');
            setSearch('');
          }}
        >
          <div className="min-w-[220px] flex-1">
            <label htmlFor="prc-search" className="mb-1 block text-xs font-semibold text-ink-secondary">
              Cari PKS / Kategori
            </label>
            <SearchField
              id="prc-search"
              value={search}
              onChange={setSearch}
              placeholder="PKS-PKC-01 atau TBS Swadaya..."
            />
          </div>
          <div className="min-w-[200px]">
            <label htmlFor="prc-status" className="mb-1 block text-xs font-semibold text-ink-secondary">
              Status Alur Harga
            </label>
            <Select id="prc-status" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">Semua Status</option>
              <option value="DRAFT">DRAFT</option>
              <option value="PENDING_VERIFICATION">PENDING_VERIFICATION</option>
              <option value="VERIFIED">VERIFIED</option>
              <option value="PUBLISHED">PUBLISHED</option>
              <option value="REJECTED">REJECTED</option>
              <option value="REVOKED">REVOKED</option>
            </Select>
          </div>
        </FilterPanel>
      }
      formSlot={
        canCreate ? (
          <div className="grid grid-cols-1 gap-6 xl:grid-cols-12">
            <div className="xl:col-span-8">
              <FormSection
                stepNumber="PRC-01"
                title="Input Draf Harga Pembelian PKS"
                description="Kutipan baru berstatus DRAFT dan tidak langsung tampil di Portal Publik sebelum diverifikasi checker."
              >
                <form onSubmit={(e) => void handleCreateDraft(e)} className="space-y-3">
                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                    <FormField id="prc-mill" label="PKS Mitra" required>
                      <Select id="prc-mill" value={millId || mills[0]?.id || ''} onChange={(e) => setMillId(e.target.value)}>
                        {mills.map((m) => (
                          <option key={m.id} value={m.id}>
                            {m.mill_code} - {m.mill_name}
                          </option>
                        ))}
                      </Select>
                    </FormField>
                    <FormField id="prc-cat" label="Kategori Mutu" required>
                      <Select id="prc-cat" value={categoryId || categories[0]?.id || ''} onChange={(e) => setCategoryId(e.target.value)}>
                        {categories.map((c) => (
                          <option key={c.id} value={c.id}>
                            {c.name}
                          </option>
                        ))}
                      </Select>
                    </FormField>
                    <FormField id="prc-src" label="Sumber Data Harga" required>
                      <Select id="prc-src" value={sourceId || sources[0]?.id || ''} onChange={(e) => setSourceId(e.target.value)}>
                        {sources.map((s) => (
                          <option key={s.id} value={s.id}>
                            {s.source_name}
                          </option>
                        ))}
                      </Select>
                    </FormField>
                  </div>

                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                    <FormField id="prc-amount" label="Nominal (Rp/kg)" required>
                      <Input
                        id="prc-amount"
                        monospace
                        value={pricePerKg}
                        onChange={(e) => setPricePerKg(e.target.value)}
                      />
                    </FormField>
                    <FormField id="prc-from" label="Berlaku Mulai" required>
                      <Input
                        id="prc-from"
                        type="datetime-local"
                        value={effectiveFrom}
                        onChange={(e) => setEffectiveFrom(e.target.value)}
                      />
                    </FormField>
                    <FormField id="prc-until" label="Berlaku Hingga">
                      <Input
                        id="prc-until"
                        type="datetime-local"
                        value={effectiveUntil}
                        onChange={(e) => setEffectiveUntil(e.target.value)}
                      />
                    </FormField>
                  </div>

                  <FormField id="prc-notes" label="Catatan Sumber / Penyesuaian">
                    <Input
                      id="prc-notes"
                      placeholder="Referensi surat harga atau informasi tambahan"
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                    />
                  </FormField>

                  <Button
                    type="submit"
                    isLoading={createDraft.isPending}
                    leadingIcon={<Plus aria-hidden="true" className="h-4 w-4" />}
                  >
                    Simpan Draf Harga PKS
                  </Button>
                </form>
              </FormSection>
            </div>

            <div className="xl:col-span-4">
              <FormSection
                stepNumber="BR-004"
                title="Input Acuan Resmi Disbun"
                description="Tercatat terpisah dari penawaran PKS ({disbunList.length} aktif)."
              >
                <form onSubmit={(e) => void handleCreateDisbun(e)} className="space-y-3">
                  <FormField id="disbun-cat" label="Kategori Umur Tanaman" required>
                    <Select
                      id="disbun-cat"
                      value={disbunCategoryId || categories[0]?.id || ''}
                      onChange={(e) => setDisbunCategoryId(e.target.value)}
                    >
                      {categories.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.name} ({c.age_group ?? '-'})
                        </option>
                      ))}
                    </Select>
                  </FormField>
                  <FormField id="disbun-amt" label="Harga Resmi Disbun (Rp/kg)" required>
                    <Input
                      id="disbun-amt"
                      monospace
                      value={disbunPrice}
                      onChange={(e) => setDisbunPrice(e.target.value)}
                    />
                  </FormField>
                  <Button type="submit" variant="secondary" isLoading={createDisbun.isPending} fullWidth>
                    Catat Harga Acuan Disbun ({disbunList.length})
                  </Button>
                </form>
              </FormSection>
            </div>
          </div>
        ) : null
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

      {pricesQuery.isError ? (
        <StateFeedbackCard
          variant="error"
          error={pricesQuery.error}
          onAction={() => void pricesQuery.refetch()}
        />
      ) : (
        <DataTable<InternalPriceQuote>
          caption="Daftar Kutipan Harga Internal Multi-PKS"
          rows={quotes}
          isLoading={pricesQuery.isLoading}
          getRowKey={(q) => q.id}
          columns={[
            {
              key: 'mill',
              header: 'PKS & Kategori',
              render: (q) => (
                <div>
                  <p className="font-mono text-xs font-bold text-primary-default">{q.mill_code}</p>
                  <p className="font-semibold text-ink-primary">{q.mill_name}</p>
                  <p className="text-xs text-text-muted">{q.price_category_name}</p>
                </div>
              ),
            },
            {
              key: 'price',
              header: 'Harga & Periode',
              align: 'right',
              render: (q) => (
                <div>
                  <p className="font-mono text-base font-bold text-ink-primary">
                    {formatPricePerKg(q.price_per_kg)}
                  </p>
                  <p className="text-xs text-text-muted">
                    Mulai: {formatWibDateTime(q.effective_from)}
                  </p>
                </div>
              ),
            },
            {
              key: 'status',
              header: 'Status & SoD',
              render: (q) => (
                <div className="space-y-1">
                  <StatusIndicator status={q.display_status} />
                  {q.is_simulation ? <Badge tone="warning">Simulasi</Badge> : null}
                  {q.submitted_by === user.id && q.status === 'PENDING_VERIFICATION' ? (
                    <p className="flex items-center gap-1 text-[11px] font-semibold text-warning-text">
                      <ShieldAlert aria-hidden="true" className="h-3.5 w-3.5" />
                      <span>Pengaju tidak dapat memverifikasi sendiri</span>
                    </p>
                  ) : null}
                </div>
              ),
            },
            {
              key: 'actions',
              header: 'Aksi Workflow',
              render: (q) => (
                <div className="flex flex-wrap gap-2">
                  {(q.status === 'DRAFT' || q.status === 'REJECTED') && canCreate ? (
                    <Button
                      size="sm"
                      variant="outline"
                      isLoading={submitPrice.isPending}
                      leadingIcon={<Send aria-hidden="true" className="h-3.5 w-3.5" />}
                      onClick={() =>
                        void runSimpleTransition(
                          () => submitPrice.mutateAsync(q.id),
                          `Harga ${q.mill_code} diajukan ke verifikator.`,
                        )
                      }
                    >
                      Ajukan Verifikasi
                    </Button>
                  ) : null}

                  {q.status === 'PENDING_VERIFICATION' && canVerify ? (
                    q.submitted_by === user.id ? (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() =>
                          void runSimpleTransition(
                            () =>
                              verifyPrice.mutateAsync({
                                priceQuoteId: q.id,
                                payload: { decision: 'APPROVE', reason: null },
                              }),
                            'Verifikasi',
                          )
                        }
                      >
                        Uji Blokir Self-Verify
                      </Button>
                    ) : (
                      <>
                        <Button
                          size="sm"
                          variant="primary"
                          isLoading={verifyPrice.isPending}
                          leadingIcon={<Check aria-hidden="true" className="h-3.5 w-3.5" />}
                          onClick={() =>
                            void runSimpleTransition(
                              () =>
                                verifyPrice.mutateAsync({
                                  priceQuoteId: q.id,
                                  payload: { decision: 'APPROVE', reason: 'Terverifikasi checker' },
                                }),
                              `Harga ${q.mill_code} terverifikasi.`,
                            )
                          }
                        >
                          Setujui Verifikasi
                        </Button>
                        <Button
                          size="sm"
                          variant="danger"
                          onClick={() => setDialogAction({ kind: 'reject', quote: q })}
                        >
                          Tolak
                        </Button>
                      </>
                    )
                  ) : null}

                  {q.status === 'VERIFIED' && canPublish ? (
                    <Button
                      size="sm"
                      variant="primary"
                      isLoading={publishPrice.isPending}
                      onClick={() =>
                        void runSimpleTransition(
                          () => publishPrice.mutateAsync(q.id),
                          `Harga ${q.mill_code} dipublikasikan ke Portal Publik.`,
                        )
                      }
                    >
                      Publikasikan
                    </Button>
                  ) : null}

                  {q.status === 'PUBLISHED' && canRevoke ? (
                    <Button
                      size="sm"
                      variant="ghost"
                      leadingIcon={<XCircle aria-hidden="true" className="h-3.5 w-3.5" />}
                      onClick={() => setDialogAction({ kind: 'revoke', quote: q })}
                    >
                      Cabut
                    </Button>
                  ) : null}
                </div>
              ),
            },
          ]}
        />
      )}

      <ConfirmDialog
        open={Boolean(dialogAction)}
        title={
          dialogAction?.kind === 'reject'
            ? `Tolak Verifikasi Harga ${dialogAction?.quote.mill_code}?`
            : `Cabut Publikasi Harga ${dialogAction?.quote.mill_code}?`
        }
        description="Tindakan ini mengubah status harga dan mencatat alasan resmi pada riwayat audit."
        requireReason
        confirmLabel={dialogAction?.kind === 'reject' ? 'Tolak Kutipan' : 'Cabut Harga'}
        tone="danger"
        isSubmitting={verifyPrice.isPending || revokePrice.isPending}
        onConfirm={handleConfirmDialog}
        onCancel={() => setDialogAction(null)}
      />
    </DataManagementTemplate>
  );
}
