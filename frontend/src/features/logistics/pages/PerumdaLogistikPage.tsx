import { useState } from 'react';
import { Badge, Button, Select } from '@/components/atoms';
import { PolicyNoticeBanner, StatusIndicator } from '@/components/molecules';
import {
  ConfirmDialog,
  DataTable,
  FilterPanel,
  FormSection,
  StateFeedbackCard,
  StatusTimeline,
} from '@/components/organisms';
import { DataManagementTemplate } from '@/components/templates';
import { hasPermission, type AuthenticatedUser } from '@/lib/auth/permissions';
import { formatKg, formatWibDateTime } from '@/lib/decimal/precision';
import { ApiError } from '@/lib/errors/errorCatalog';
import { useUiStore } from '@/lib/state/uiStore';
import {
  useCancelDeliveryOrder,
  useDeliveryOrders,
  useTransitionDeliveryStatus,
  type DeliveryOrder,
} from '../api/logisticsApi';

export function PerumdaLogistikPage({ user }: { readonly user: AuthenticatedUser }) {
  const pushToast = useUiStore((s) => s.pushToast);
  const canTransition = hasPermission(user, 'delivery_orders.transition');
  const canCancel = hasPermission(user, 'delivery_orders.cancel');

  const [statusFilter, setStatusFilter] = useState('');
  const [selectedDoId, setSelectedDoId] = useState<string | null>(null);
  const [cancelTarget, setCancelTarget] = useState<DeliveryOrder | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const dosQuery = useDeliveryOrders({ status: statusFilter });
  const transitionDo = useTransitionDeliveryStatus();
  const cancelDo = useCancelDeliveryOrder();

  const items = dosQuery.data?.data ?? [];
  const selectedDo = items.find((d) => d.id === selectedDoId) ?? items[0] ?? null;

  const handleMarkInTransit = async (item: DeliveryOrder) => {
    setActionError(null);
    try {
      await transitionDo.mutateAsync({
        deliveryOrderId: item.id,
        payload: { target_status: 'IN_TRANSIT', reason: 'Konfirmasi keberangkatan Perumda', version: item.version },
      });
      pushToast({ tone: 'info', title: `${item.delivery_order_number} dalam perjalanan.` });
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
        eyebrow: 'PORTAL PERUMDA | MONITORING LOGISTIK',
        title: 'Pengawasan Pengiriman & Surat Jalan e-DO',
        description:
          'Pantau seluruh pengiriman lintas koperasi menuju PKS mitra beserta jejak asal penerimaan TBS dan histori perubahan status.',
      }}
      noticeSlot={
        <PolicyNoticeBanner
          kind="info"
          title="Status Logistik Terverifikasi Tanpa GPS Real-Time (PRD §3.3)"
          description="Pelacakan armada menggunakan bukti status e-DO tervalidasi (READY, IN_TRANSIT, ARRIVED, RECEIVED, COMPLETED) dan perubahan pascamuat wajib beralasan audit (BR-015)."
        />
      }
      filterSlot={
        <FilterPanel onReset={() => setStatusFilter('')}>
          <div className="min-w-[220px]">
            <label htmlFor="log-status" className="mb-1 block text-xs font-semibold text-ink-secondary">
              Filter Status e-DO
            </label>
            <Select id="log-status" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="">Semua Status</option>
              <option value="DRAFT">DRAFT</option>
              <option value="READY">READY</option>
              <option value="IN_TRANSIT">IN_TRANSIT</option>
              <option value="ARRIVED">ARRIVED</option>
              <option value="RECEIVED">RECEIVED</option>
              <option value="COMPLETED">COMPLETED</option>
              <option value="CANCELLED">CANCELLED</option>
            </Select>
          </div>
        </FilterPanel>
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
          {dosQuery.isError ? (
            <StateFeedbackCard
              variant="error"
              error={dosQuery.error}
              onAction={() => void dosQuery.refetch()}
            />
          ) : (
            <DataTable<DeliveryOrder>
              caption="Daftar Pengiriman TBS Perumda"
              rows={items}
              isLoading={dosQuery.isLoading}
              getRowKey={(d) => d.id}
              columns={[
                {
                  key: 'edo',
                  header: 'e-DO & Tujuan PKS',
                  render: (d) => (
                    <button
                      type="button"
                      onClick={() => setSelectedDoId(d.id)}
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
                  key: 'origin',
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
                      {d.status === 'READY' && canTransition ? (
                        <Button size="sm" variant="outline" onClick={() => void handleMarkInTransit(d)}>
                          Tandai Jalan
                        </Button>
                      ) : null}
                      {['DRAFT', 'READY', 'IN_TRANSIT'].includes(d.status) && canCancel ? (
                        <Button size="sm" variant="ghost" onClick={() => setCancelTarget(d)}>
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

        <div className="min-w-0 xl:col-span-5">
          {selectedDo ? (
            <FormSection
              stepNumber="TRACK"
              title={selectedDo.delivery_order_number}
              description={`${selectedDo.mill_name} | ${selectedDo.vehicle_plate}`}
              aside={<StatusIndicator status={selectedDo.status} />}
            >
              <div className="flex flex-wrap items-center gap-2 text-xs text-ink-secondary">
                <Badge tone="neutral">
                  GPS Real-Time: {selectedDo.gps_tracking_supported ? 'Ya' : 'Tidak (Non-MVP)'}
                </Badge>
                {selectedDo.issued_at ? (
                  <span>Terbit: {formatWibDateTime(selectedDo.issued_at)}</span>
                ) : null}
              </div>

              <StatusTimeline
                events={selectedDo.status_events.map((ev) => ({
                  id: ev.id,
                  status: ev.new_status,
                  timestamp: ev.event_time,
                  actor: ev.actor_id,
                  note: ev.reason,
                }))}
              />
            </FormSection>
          ) : null}
        </div>
      </div>

      <ConfirmDialog
        open={Boolean(cancelTarget)}
        title={`Batalkan e-DO ${cancelTarget?.delivery_order_number ?? ''}?`}
        description="Pembatalan pengiriman harus menyertakan alasan jelas untuk jejak audit Perumda."
        requireReason
        confirmLabel="Batalkan Pengiriman"
        tone="danger"
        isSubmitting={cancelDo.isPending}
        onConfirm={async (reason) => {
          if (!cancelTarget) return;
          try {
            await cancelDo.mutateAsync({
              deliveryOrderId: cancelTarget.id,
              reason,
              version: cancelTarget.version,
            });
            pushToast({ tone: 'info', title: `e-DO ${cancelTarget.delivery_order_number} dibatalkan.` });
            setCancelTarget(null);
          } catch (error) {
            if (error instanceof ApiError) {
              setActionError(`${error.code}: ${error.message}`);
            }
            setCancelTarget(null);
          }
        }}
        onCancel={() => setCancelTarget(null)}
      />
    </DataManagementTemplate>
  );
}
