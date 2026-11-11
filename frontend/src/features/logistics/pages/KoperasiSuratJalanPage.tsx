import { FileCheck2, Lock, QrCode, Send, Truck } from 'lucide-react';
import { useState } from 'react';
import { Badge, Button, Input, Select } from '@/components/atoms';
import { FormField, PolicyNoticeBanner, StatusIndicator } from '@/components/molecules';
import {
  ConfirmDialog,
  DataTable,
  FormSection,
  StateFeedbackCard,
  StatusTimeline,
} from '@/components/organisms';
import { TransactionTemplate } from '@/components/templates';
import {
  useDrivers,
  useMills,
  useVehicles,
} from '@/features/master-data/api/masterDataApi';
import { useReceipts } from '@/features/receiving/api/receivingApi';
import { hasPermission, type AuthenticatedUser } from '@/lib/auth/permissions';
import { formatKg, formatWibDateTime } from '@/lib/decimal/precision';
import { ApiError } from '@/lib/errors/errorCatalog';
import { useUiStore } from '@/lib/state/uiStore';
import {
  useCancelDeliveryOrder,
  useContracts,
  useCreateDeliveryOrderDraft,
  useDeliveryOrders,
  useIssueDeliveryOrder,
  useTransitionDeliveryStatus,
  type DeliveryOrder,
} from '../api/logisticsApi';

export function KoperasiSuratJalanPage({ user }: { readonly user: AuthenticatedUser }) {
  const pushToast = useUiStore((s) => s.pushToast);

  const canCreate = hasPermission(user, 'delivery_orders.create');
  const canIssue = hasPermission(user, 'delivery_orders.issue');
  const canTransition = hasPermission(user, 'delivery_orders.transition');
  const canCancel = hasPermission(user, 'delivery_orders.cancel');
  const canReadContracts = hasPermission(user, 'contracts.read');

  const receiptsQuery = useReceipts();
  const millsQuery = useMills();
  const contractsQuery = useContracts(canReadContracts);
  const vehiclesQuery = useVehicles();
  const driversQuery = useDrivers();
  const dosQuery = useDeliveryOrders();

  const createDo = useCreateDeliveryOrderDraft();
  const issueDo = useIssueDeliveryOrder();
  const transitionDo = useTransitionDeliveryStatus();
  const cancelDo = useCancelDeliveryOrder();

  const receipts = receiptsQuery.data?.data ?? [];
  const mills = millsQuery.data?.data ?? [];
  const contracts = contractsQuery.data?.data ?? [];
  const vehicles = vehiclesQuery.data?.data ?? [];
  const drivers = driversQuery.data?.data ?? [];
  const deliveryOrders = dosQuery.data?.data ?? [];

  const assignedContractIds = Array.from(new Set(deliveryOrders.map((d) => d.contract_id)));

  const [selectedReceiptIds, setSelectedReceiptIds] = useState<string[]>([]);
  const [millId, setMillId] = useState('');
  const [contractId, setContractId] = useState('');
  const [vehicleId, setVehicleId] = useState('');
  const [driverId, setDriverId] = useState('');
  const [activeDoId, setActiveDoId] = useState<string | null>(null);
  const [doToCancel, setDoToCancel] = useState<DeliveryOrder | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const selectedDo = deliveryOrders.find((d) => d.id === activeDoId) ?? deliveryOrders[0] ?? null;

  const toggleReceipt = (id: string) => {
    setSelectedReceiptIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id],
    );
  };

  const handleCreateDraft = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    if (selectedReceiptIds.length === 0) {
      setActionError('Pilih minimal satu penerimaan berstatus Tervalidasi (VALIDATED).');
      return;
    }
    const chosenMill = millId || mills[0]?.id;
    const chosenContract =
      contractId ||
      contracts.find((c) => c.status === 'ACTIVE')?.id ||
      contracts[0]?.id ||
      assignedContractIds[0];
    const chosenVehicle = vehicleId || vehicles[0]?.id;
    const chosenDriver = driverId || drivers[0]?.id;
    if (!chosenMill || !chosenContract || !chosenVehicle || !chosenDriver) {
      setActionError('Lengkapi PKS tujuan, kontrak aktif, kendaraan, dan supir.');
      return;
    }
    try {
      const res = await createDo.mutateAsync({
        mill_id: chosenMill,
        contract_id: chosenContract,
        vehicle_id: chosenVehicle,
        driver_id: chosenDriver,
        receipt_ids: selectedReceiptIds,
      });
      setSelectedReceiptIds([]);
      setActiveDoId(res.data.id);
      pushToast({
        tone: 'success',
        title: `Draf e-DO ${res.data.delivery_order_number} dibuat (${formatKg(res.data.total_origin_weight_kg)}).`,
        requestId: res.request_id,
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const handleIssue = async (item: DeliveryOrder) => {
    setActionError(null);
    try {
      const res = await issueDo.mutateAsync({
        deliveryOrderId: item.id,
        version: item.version,
      });
      pushToast({
        tone: 'success',
        title: `e-DO ${res.data.delivery_order_number} resmi diterbitkan (QR: ${res.data.qr_verification_token}).`,
        requestId: res.request_id,
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const handleDepart = async (item: DeliveryOrder) => {
    setActionError(null);
    try {
      await transitionDo.mutateAsync({
        deliveryOrderId: item.id,
        payload: { target_status: 'IN_TRANSIT', reason: 'Truk berangkat dari TPS koperasi', version: item.version },
      });
      pushToast({ tone: 'info', title: `${item.delivery_order_number} berstatus Dalam Perjalanan.` });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const handleConfirmCancel = async (reason: string) => {
    if (!doToCancel) return;
    setActionError(null);
    try {
      await cancelDo.mutateAsync({
        deliveryOrderId: doToCancel.id,
        reason,
        version: doToCancel.version,
      });
      pushToast({ tone: 'info', title: `e-DO ${doToCancel.delivery_order_number} dibatalkan.` });
      setDoToCancel(null);
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
      setDoToCancel(null);
    }
  };

  return (
    <>
      <TransactionTemplate
        user={user}
        header={{
          eyebrow: 'PORTAL KOPERASI | SURAT JALAN ELEKTRONIK (e-DO)',
          title: 'Penyusunan & Penerbitan e-DO Konsolidasi',
          description:
            'Gabungkan penerimaan TBS tervalidasi ke dalam satu e-DO resmi, cadangkan kuota kontrak, dan tampilkan token QR verifikasi PKS.',
        }}
        noticeSlot={
          <PolicyNoticeBanner
            kind="pending_sop"
            title="Kewenangan Penerbitan e-DO & Batasan GPS (AFD §41 #1 & PRD §3.3)"
            description="Penerbitan e-DO oleh operator koperasi mengikuti aturan simulasi menunggu penetapan SOP Perumda. Sistem tidak menyediakan pelacakan GPS real-time kendaraan; pelacakan dilakukan melalui perpindahan status e-DO."
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
                stepNumber="LOG-01"
                title="Konsolidasi Penerimaan Tervalidasi ke e-DO Baru"
                description="Satu transaksi penerimaan tidak dapat dialokasikan ganda ke pengiriman aktif (BR-012)."
              >
                <form onSubmit={(e) => void handleCreateDraft(e)} className="space-y-4">
                  <div className="space-y-2">
                    <p className="text-xs font-bold uppercase tracking-wide text-ink-secondary">
                      Pilih Penerimaan Asal (VALIDATED)
                    </p>
                    <div className="max-h-52 space-y-1.5 overflow-y-auto rounded-md border border-border-subtle p-3">
                      {receipts.map((r) => {
                        const alreadyLocked = ['ALLOCATED', 'SHIPPED', 'CLOSED', 'CANCELLED'].includes(r.status);
                        const isReady = r.status === 'VALIDATED';
                        const checked = selectedReceiptIds.includes(r.id);
                        return (
                          <label
                            key={r.id}
                            className={`flex min-h-[44px] items-center justify-between gap-2 rounded px-2.5 py-1.5 text-xs ${
                              isReady ? 'cursor-pointer hover:bg-surface-subtle' : 'opacity-65'
                            }`}
                          >
                            <span className="flex items-center gap-2">
                              <input
                                type="checkbox"
                                checked={checked}
                                disabled={!isReady && !alreadyLocked}
                                onChange={() => toggleReceipt(r.id)}
                                className="h-4 w-4 accent-primary-default"
                              />
                              <span className="font-mono font-bold">{r.receipt_number}</span>
                              <span>{r.farmer_name}</span>
                            </span>
                            <span className="flex items-center gap-2">
                              <span className="font-mono font-semibold">
                                {formatKg(r.current_weighing?.net_weight_kg)}
                              </span>
                              {alreadyLocked ? (
                                <Badge tone="neutral">
                                  <Lock aria-hidden="true" className="h-3 w-3" />
                                  {r.status}
                                </Badge>
                              ) : (
                                <StatusIndicator status={r.status} />
                              )}
                            </span>
                          </label>
                        );
                      })}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                    <FormField id="edo-mill" label="PKS Tujuan (Pilihan Terkontrol)" required>
                      <Select id="edo-mill" value={millId || mills[0]?.id || ''} onChange={(e) => setMillId(e.target.value)}>
                        {mills.map((m) => (
                          <option key={m.id} value={m.id}>
                            {m.mill_code} - {m.mill_name}
                          </option>
                        ))}
                      </Select>
                    </FormField>
                    <FormField
                      id="edo-contract"
                      label="Referensi Kontrak Tujuan"
                      required
                      helperText={
                        !canReadContracts && assignedContractIds.length === 0
                          ? 'Koperasi menerima ID penugasan kontrak dari Perumda (tanpa akses rincian harga/kuota komersial).'
                          : undefined
                      }
                    >
                      {!canReadContracts && assignedContractIds.length === 0 ? (
                        <Input
                          id="edo-contract"
                          monospace
                          value={contractId}
                          onChange={(e) => setContractId(e.target.value)}
                          placeholder="UUID Kontrak penugasan (contoh: 70000000-...)"
                          required
                        />
                      ) : (
                        <Select
                          id="edo-contract"
                          value={contractId || contracts[0]?.id || assignedContractIds[0] || ''}
                          onChange={(e) => setContractId(e.target.value)}
                        >
                          {canReadContracts
                            ? contracts.map((c) => (
                                <option key={c.id} value={c.id}>
                                  {c.contract_number} ({c.status})
                                </option>
                              ))
                            : assignedContractIds.map((cid, idx) => (
                                <option key={cid} value={cid}>
                                  Kontrak Terkait Penugasan #{idx + 1} ({cid.slice(-6)})
                                </option>
                              ))}
                        </Select>
                      )}
                    </FormField>
                    <FormField id="edo-veh" label="Kendaraan" required>
                      <Select id="edo-veh" value={vehicleId || vehicles[0]?.id || ''} onChange={(e) => setVehicleId(e.target.value)}>
                        {vehicles.map((v) => (
                          <option key={v.id} value={v.id}>
                            {v.plate_number} - {v.vehicle_type}
                          </option>
                        ))}
                      </Select>
                    </FormField>
                    <FormField id="edo-drv" label="Supir" required>
                      <Select id="edo-drv" value={driverId || drivers[0]?.id || ''} onChange={(e) => setDriverId(e.target.value)}>
                        {drivers.map((d) => (
                          <option key={d.id} value={d.id}>
                            {d.full_name}
                          </option>
                        ))}
                      </Select>
                    </FormField>
                  </div>

                  <Button
                    type="submit"
                    isLoading={createDo.isPending}
                    leadingIcon={<FileCheck2 aria-hidden="true" className="h-4 w-4" />}
                  >
                    Susun Draf e-DO
                  </Button>
                </form>
              </FormSection>
            ) : null}

            {dosQuery.isError ? (
              <StateFeedbackCard
                variant="error"
                error={dosQuery.error}
                onAction={() => void dosQuery.refetch()}
              />
            ) : (
              <DataTable<DeliveryOrder>
                caption="Daftar Surat Jalan e-DO Koperasi"
                rows={deliveryOrders}
                isLoading={dosQuery.isLoading}
                getRowKey={(d) => d.id}
                columns={[
                  {
                    key: 'num',
                    header: 'Nomor e-DO & PKS',
                    render: (d) => (
                      <button
                        type="button"
                        onClick={() => setActiveDoId(d.id)}
                        className="text-left hover:underline"
                      >
                        <p className="font-mono text-xs font-bold text-primary-default">
                          {d.delivery_order_number}
                        </p>
                        <p className="font-semibold text-ink-primary">{d.mill_name}</p>
                        <p className="text-xs text-text-muted">
                          {d.vehicle_plate} | {d.driver_name}
                        </p>
                      </button>
                    ),
                  },
                  {
                    key: 'weight',
                    header: 'Berat Muat Asal',
                    align: 'right',
                    render: (d) => (
                      <span className="font-mono font-bold">
                        {formatKg(d.total_origin_weight_kg)}
                      </span>
                    ),
                  },
                  {
                    key: 'status',
                    header: 'Status',
                    render: (d) => <StatusIndicator status={d.status} />,
                  },
                  {
                    key: 'actions',
                    header: 'Aksi',
                    render: (d) => (
                      <div className="flex flex-wrap gap-2">
                        {d.status === 'DRAFT' && canIssue ? (
                          <Button
                            size="sm"
                            variant="primary"
                            isLoading={issueDo.isPending}
                            leadingIcon={<Send aria-hidden="true" className="h-3.5 w-3.5" />}
                            onClick={() => void handleIssue(d)}
                          >
                            Terbitkan e-DO
                          </Button>
                        ) : null}
                        {d.status === 'READY' && canTransition ? (
                          <Button
                            size="sm"
                            variant="secondary"
                            isLoading={transitionDo.isPending}
                            leadingIcon={<Truck aria-hidden="true" className="h-3.5 w-3.5" />}
                            onClick={() => void handleDepart(d)}
                          >
                            Berangkat
                          </Button>
                        ) : null}
                        {['DRAFT', 'READY', 'IN_TRANSIT'].includes(d.status) && canCancel ? (
                          <Button size="sm" variant="ghost" onClick={() => setDoToCancel(d)}>
                            Batalkan
                          </Button>
                        ) : null}
                      </div>
                    ),
                  },
                ]}
              />
            )}
          </div>
        }
        secondarySlot={
          selectedDo ? (
            <FormSection
              stepNumber="QR"
              title={`Detail e-DO: ${selectedDo.delivery_order_number}`}
              description={`Tujuan: ${selectedDo.mill_name}`}
              aside={<StatusIndicator status={selectedDo.status} />}
            >
              <div className="rounded-md border border-border-subtle bg-surface-subtle/70 p-4">
                <div className="flex items-center gap-2 text-primary-default">
                  <QrCode aria-hidden="true" className="h-5 w-5" />
                  <p className="text-xs font-bold uppercase">Token Verifikasi Terkendali PKS</p>
                </div>
                <p className="mt-1.5 font-mono text-sm font-bold text-ink-primary">
                  {selectedDo.qr_verification_token}
                </p>
                <p className="mt-1 text-xs text-text-muted">
                  Token ini terproteksi RBAC: hanya petugas PKS tujuan yang dapat memverifikasi
                  kedatangan e-DO (PRD FR-LOG-003).
                </p>
              </div>

              <div className="space-y-2">
                <p className="text-xs font-bold uppercase text-ink-secondary">
                  Rincian Muatan ({selectedDo.lines.length} Penerimaan Asal)
                </p>
                <ul className="divide-y divide-border-subtle rounded-md border border-border-subtle text-xs">
                  {selectedDo.lines.map((ln) => (
                    <li key={ln.id} className="flex items-center justify-between px-3 py-2">
                      <div>
                        <p className="font-mono font-semibold text-primary-default">
                          {ln.receipt_number}
                        </p>
                        <p className="text-ink-secondary">{ln.farmer_name}</p>
                      </div>
                      <span className="font-mono font-bold">
                        {formatKg(ln.origin_weight_snapshot_kg)}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="space-y-2 pt-2">
                <p className="text-xs font-bold uppercase text-ink-secondary">Riwayat Status</p>
                <StatusTimeline
                  events={selectedDo.status_events.map((ev) => ({
                    id: ev.id,
                    status: ev.new_status,
                    timestamp: ev.event_time,
                    actor: ev.actor_id,
                    note: ev.reason,
                  }))}
                />
                {selectedDo.issued_at ? (
                  <p className="text-[11px] text-text-muted">
                    Diterbitkan: {formatWibDateTime(selectedDo.issued_at)}
                  </p>
                ) : null}
              </div>
            </FormSection>
          ) : null
        }
      />

      <ConfirmDialog
        open={Boolean(doToCancel)}
        title={`Batalkan e-DO ${doToCancel?.delivery_order_number ?? ''}?`}
        description="Pembatalan akan melepaskan penerimaan asal dan mengembalikan sisa kuota kontrak dengan catatan alasan audit."
        requireReason
        confirmLabel="Batalkan e-DO"
        tone="danger"
        isSubmitting={cancelDo.isPending}
        onConfirm={handleConfirmCancel}
        onCancel={() => setDoToCancel(null)}
      />
    </>
  );
}
