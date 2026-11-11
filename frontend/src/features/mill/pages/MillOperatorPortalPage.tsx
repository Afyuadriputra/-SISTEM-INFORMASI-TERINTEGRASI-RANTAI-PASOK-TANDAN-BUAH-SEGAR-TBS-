import { Link } from '@tanstack/react-router';
import { QrCode, ShieldCheck } from 'lucide-react';
import { useState } from 'react';
import { Button, Input } from '@/components/atoms';
import { FormField, PolicyNoticeBanner, StatusIndicator } from '@/components/molecules';
import { DataTable, FormSection, KPIGrid, StateFeedbackCard, type KPIItem } from '@/components/organisms';
import { DashboardTemplate } from '@/components/templates';
import {
  useDeliveryOrders,
  useVerifyDeliveryQr,
  type DeliveryOrder,
} from '@/features/logistics/api/logisticsApi';
import type { AuthenticatedUser } from '@/lib/auth/permissions';
import { formatKg, formatWibDateTime } from '@/lib/decimal/precision';
import { ApiError } from '@/lib/errors/errorCatalog';
import { useUiStore } from '@/lib/state/uiStore';

export function MillOperatorPortalPage({ user }: { readonly user: AuthenticatedUser }) {
  const pushToast = useUiStore((s) => s.pushToast);
  const dosQuery = useDeliveryOrders();
  const verifyQr = useVerifyDeliveryQr();

  const [qrInput, setQrInput] = useState('');
  const [plateInput, setPlateInput] = useState('');
  const [actionError, setActionError] = useState<string | null>(null);

  const deliveryOrders = dosQuery.data?.data ?? [];

  const handleVerifyArrival = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    if (!qrInput.trim()) {
      setActionError('Masukkan nomor e-DO atau token QR kedatangan truk.');
      return;
    }
    try {
      const res = await verifyQr.mutateAsync({
        qr_token_or_edo_number: qrInput.trim(),
        observed_plate_number: plateInput.trim() || null,
      });
      setQrInput('');
      setPlateInput('');
      pushToast({
        tone: 'success',
        title: `Kedatangan ${res.data.delivery_order_number} terverifikasi (${res.data.vehicle_plate}).`,
        requestId: res.request_id,
      });
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const kpis: KPIItem[] = [
    {
      id: 'mill-incoming',
      label: 'Pengiriman Menuju PKS Anda',
      value: String(deliveryOrders.length),
      hint: 'Terisolasi sesuai cakupan mill_id',
    },
    {
      id: 'mill-transit',
      label: 'Dalam Perjalanan / Siap',
      value: String(
        deliveryOrders.filter((d) => ['READY', 'IN_TRANSIT'].includes(d.status)).length,
      ),
      tone: 'warning',
    },
    {
      id: 'mill-arrived',
      label: 'Tiba / Diterima PKS',
      value: String(
        deliveryOrders.filter((d) => ['ARRIVED', 'RECEIVED', 'COMPLETED'].includes(d.status))
          .length,
      ),
      tone: 'primary',
    },
    {
      id: 'mill-approach',
      label: 'Metode Input PKS',
      value: 'Pendekatan A',
      hint: 'Input manual terverifikasi (DEC-009)',
    },
  ];

  return (
    <DashboardTemplate
      user={user}
      header={{
        eyebrow: 'PORTAL PKS | VERIFIKASI KEDATANGAN e-DO',
        title: 'Dashboard & Verifikasi Kedatangan TBS PKS',
        description:
          'Verifikasi surat jalan e-DO atau kode QR yang ditujukan khusus ke PKS Anda sebelum mencatat tiket jembatan timbang.',
        actions: (
          <Link
            to="/app/pks/tiket-timbang"
            className="inline-flex min-h-[44px] items-center rounded-md bg-primary-default px-4 text-sm font-semibold text-primary-foreground hover:bg-brand-hover"
          >
            Catat Tiket Timbang PKS
          </Link>
        ),
      }}
      noticeSlot={
        <PolicyNoticeBanner
          kind="info"
          title="Isolasi Cakupan PKS & QR Terkendali (BR-PKS-001 & FR-LOG-003)"
          description="Petugas PKS hanya dapat memverifikasi e-DO yang dialamatkan ke PKS miliknya. Token e-DO milik PKS lain otomatis ditolak (403 MILL_EDO_MILL_MISMATCH)."
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

      <FormSection
        stepNumber="PKS-QR"
        title="Verifikasi Nomor e-DO / Kode QR Kedatangan"
        description="Konfirmasi kesesuaian e-DO dengan kendaraan di gerbang timbang pabrik."
      >
        <form onSubmit={(e) => void handleVerifyArrival(e)} className="grid grid-cols-1 gap-3 sm:grid-cols-12 sm:items-end">
          <div className="sm:col-span-5">
            <FormField id="pks-qr-input" label="Token QR / Nomor e-DO" required>
              <Input
                id="pks-qr-input"
                monospace
                placeholder="Contoh: EDO-2026-1110-043"
                value={qrInput}
                onChange={(e) => setQrInput(e.target.value)}
              />
            </FormField>
          </div>
          <div className="sm:col-span-4">
            <FormField id="pks-plate-input" label="Plat Nomor Terpantau">
              <Input
                id="pks-plate-input"
                monospace
                placeholder="BM 9012 PL"
                value={plateInput}
                onChange={(e) => setPlateInput(e.target.value)}
              />
            </FormField>
          </div>
          <div className="sm:col-span-3">
            <Button
              type="submit"
              fullWidth
              isLoading={verifyQr.isPending}
              leadingIcon={<QrCode aria-hidden="true" className="h-4 w-4" />}
            >
              Verifikasi Tiba
            </Button>
          </div>
        </form>
      </FormSection>

      {dosQuery.isError ? (
        <StateFeedbackCard
          variant="error"
          error={dosQuery.error}
          onAction={() => void dosQuery.refetch()}
        />
      ) : (
        <DataTable<DeliveryOrder>
          caption="Daftar e-DO Tujuan PKS Ini"
          rows={deliveryOrders}
          isLoading={dosQuery.isLoading}
          getRowKey={(d) => d.id}
          columns={[
            {
              key: 'num',
              header: 'e-DO & Kendaraan',
              render: (d) => (
                <div>
                  <p className="font-mono text-xs font-bold text-primary-default">
                    {d.delivery_order_number}
                  </p>
                  <p className="text-xs font-semibold text-ink-primary">
                    {d.vehicle_plate} | {d.driver_name}
                  </p>
                  <p className="text-[11px] text-text-muted">Token: {d.qr_verification_token}</p>
                </div>
              ),
            },
            {
              key: 'weight',
              header: 'Berat Asal Koperasi',
              align: 'right',
              render: (d) => (
                <span className="font-mono font-bold">{formatKg(d.total_origin_weight_kg)}</span>
              ),
            },
            {
              key: 'status',
              header: 'Status',
              render: (d) => <StatusIndicator status={d.status} />,
            },
            {
              key: 'arrived',
              header: 'Waktu Tiba',
              render: (d) => (
                <span className="text-xs text-ink-secondary">
                  {formatWibDateTime(d.arrived_at)}
                </span>
              ),
            },
            {
              key: 'quick',
              header: 'Aksi Cepat',
              render: (d) =>
                d.status === 'IN_TRANSIT' || d.status === 'READY' ? (
                  <Button
                    size="sm"
                    variant="outline"
                    leadingIcon={<ShieldCheck aria-hidden="true" className="h-3.5 w-3.5" />}
                    onClick={() => {
                      setQrInput(d.delivery_order_number);
                      setPlateInput(d.vehicle_plate);
                    }}
                  >
                    Pilih ke Form QR
                  </Button>
                ) : (
                  <Link
                    to="/app/pks/tiket-timbang"
                    className="text-xs font-semibold text-primary-default underline"
                  >
                    Ke Tiket Timbang
                  </Link>
                ),
            },
          ]}
        />
      )}
    </DashboardTemplate>
  );
}
