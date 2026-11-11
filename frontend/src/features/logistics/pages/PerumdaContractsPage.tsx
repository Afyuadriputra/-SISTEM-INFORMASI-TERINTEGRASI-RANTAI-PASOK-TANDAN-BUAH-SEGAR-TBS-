import { Plus, ShieldCheck } from 'lucide-react';
import { useState } from 'react';
import { Badge, Button, Input, Select } from '@/components/atoms';
import { FormField, PolicyNoticeBanner, StatusIndicator } from '@/components/molecules';
import { DataTable, FormSection, StateFeedbackCard } from '@/components/organisms';
import { DataManagementTemplate } from '@/components/templates';
import { useCooperatives, useMillCompanies, useMills } from '@/features/master-data/api/masterDataApi';
import { hasPermission, type AuthenticatedUser } from '@/lib/auth/permissions';
import { isMockApiMode } from '@/lib/config/env';
import { formatCalendarOrWibDate, formatKg, formatPricePerKg } from '@/lib/decimal/precision';
import { ApiError } from '@/lib/errors/errorCatalog';
import { useUiStore } from '@/lib/state/uiStore';
import {
  useContracts,
  useCreateContract,
  useDeliveryOrders,
  useReserveQuota,
  type TradeContract,
} from '../api/logisticsApi';

export function PerumdaContractsPage({ user }: { readonly user: AuthenticatedUser }) {
  const pushToast = useUiStore((s) => s.pushToast);
  const canWrite = hasPermission(user, 'contracts.write');
  const canReserve = hasPermission(user, 'quotas.reserve');
  const canReadMillCompanies =
    hasPermission(user, 'mills.write') || user.roles.includes('DIRECTOR');

  const contractsQuery = useContracts();
  const millsQuery = useMills();
  const millCompaniesQuery = useMillCompanies(canReadMillCompanies);
  const coopsQuery = useCooperatives();
  const dosQuery = useDeliveryOrders();

  const createContract = useCreateContract();
  const reserveQuota = useReserveQuota();

  const contracts = contractsQuery.data?.data ?? [];
  const mills = millsQuery.data?.data ?? [];
  const millCompanies = millCompaniesQuery.data?.data ?? [];
  const cooperatives = coopsQuery.data?.data ?? [];
  const deliveryOrders = dosQuery.data?.data ?? [];

  const [contractNum, setContractNum] = useState('');
  const [millId, setMillId] = useState('');
  const [startDate, setStartDate] = useState('2026-11-11');
  const [endDate, setEndDate] = useState('2026-12-31');
  const [priceRuleType, setPriceRuleType] = useState<'FIXED' | 'REFERENCE_FORMULA' | 'PERIOD_SCHEDULE'>('FIXED');
  const [agreedPrice, setAgreedPrice] = useState('2850.00');
  const [businessModel, setBusinessModel] = useState<'UNCONFIRMED' | 'PRINCIPAL' | 'AGENT'>('UNCONFIRMED');
  const [initialQuotaKg, setInitialQuotaKg] = useState('50000.000');

  const [reserveContractId, setReserveContractId] = useState('');
  const [reserveDoId, setReserveDoId] = useState('');
  const [reserveKg, setReserveKg] = useState('5000.000');
  const [actionError, setActionError] = useState<string | null>(null);

  const selectedContractForQuota =
    contracts.find((c) => c.id === reserveContractId) ?? contracts[0] ?? null;

  const handleCreateContract = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    const chosenMill = mills.find((m) => m.id === (millId || mills[0]?.id));
    if (!chosenMill || !contractNum.trim()) {
      setActionError('Nomor kontrak dan PKS mitra wajib diisi.');
      return;
    }
    const millPartyId =
      millCompanies.find((mc) => mc.id === chosenMill.mill_company_id)?.party_id ??
      (isMockApiMode() ? '10000000-0000-4000-8000-000000000902' : '');
    const existingPerumdaContract = contracts.find(
      (c) => c.perumda_role === 'SELLER' || c.perumda_role === 'BUYER',
    );
    const perumdaPartyId =
      existingPerumdaContract?.perumda_role === 'SELLER'
        ? existingPerumdaContract.seller_party_id
        : existingPerumdaContract?.perumda_role === 'BUYER'
          ? existingPerumdaContract.buyer_party_id
          : (isMockApiMode() ? '10000000-0000-4000-8000-000000000901' : '');
    if (!millPartyId || !perumdaPartyId) {
      setActionError('Data party Perumda/perusahaan PKS belum tersedia dari server.');
      return;
    }
    const coopPartyId = cooperatives[0]?.party_id ?? perumdaPartyId;

    try {
      const res = await createContract.mutateAsync({
        contract_number: contractNum.trim(),
        mill_id: chosenMill.id,
        start_date: startDate,
        end_date: endDate,
        price_rule_type: priceRuleType,
        agreed_price_per_kg: priceRuleType === 'FIXED' ? Number(agreedPrice).toFixed(2) : null,
        business_model_code: businessModel,
        perumda_role:
          businessModel === 'PRINCIPAL'
            ? 'SELLER'
            : businessModel === 'AGENT'
              ? 'AGENT'
              : 'UNCONFIRMED',
        seller_party_id: businessModel === 'AGENT' ? coopPartyId : perumdaPartyId,
        buyer_party_id: millPartyId,
        agent_party_id: businessModel === 'AGENT' ? perumdaPartyId : null,
        represented_party_id: businessModel === 'AGENT' ? coopPartyId : null,
        payment_terms: 'Pembayaran penuh sesuai faktur terverifikasi (SOP Pending)',
        initial_quota_kg: Number(initialQuotaKg || '50000').toFixed(3),
      });
      pushToast({
        tone: 'success',
        title: `Kontrak ${res.data.contract_number} tersimpan (${res.data.business_model_code}).`,
        requestId: res.request_id,
      });
      setContractNum('');
    } catch (error) {
      if (error instanceof ApiError) {
        setActionError(`${error.code}: ${error.message}`);
      }
    }
  };

  const handleReserveQuota = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    if (!selectedContractForQuota) return;
    const period = selectedContractForQuota.quota_periods[0];
    const targetDoId = reserveDoId || deliveryOrders[0]?.id;
    if (!period || !targetDoId) {
      setActionError('Pilih kontrak yang memiliki periode kuota dan target e-DO.');
      return;
    }
    try {
      const res = await reserveQuota.mutateAsync({
        contractId: selectedContractForQuota.id,
        payload: {
          quota_period_id: period.id,
          delivery_order_id: targetDoId,
          reserved_weight_kg: Number(reserveKg).toFixed(3),
        },
      });
      pushToast({
        tone: 'success',
        title: `Kuota ${formatKg(res.data.reserved_weight_kg)} berhasil dicadangkan.`,
        requestId: res.request_id,
      });
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
        eyebrow: 'PORTAL PERUMDA | KONTRAK & KUOTA PKS',
        title: 'Manajemen Kontrak Niaga & Kuota Pasokan PKS',
        description:
          'Kelola kontrak perjanjian PKS, klasifikasi model usaha (Principal/Agent/Unconfirmed), serta pemantauan alokasi kuota atomik per periode.',
      }}
      noticeSlot={
        <PolicyNoticeBanner
          kind="pending_sop"
          title="Penetapan PKS Tujuan & Model Usaha (BR-KTR-003 & AFD §41)"
          description="Pemilihan PKS tujuan wajib mempertimbangkan sisa kuota, jarak, kualitas, dan syarat pembayaran secara manusiawi (tidak otomatis memilih harga tertinggi). Kontrak dengan model usaha UNCONFIRMED memblokir finalisasi keuangan nyata."
        />
      }
      formSlot={
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-12">
          {canWrite ? (
            <div className="xl:col-span-7">
              <FormSection stepNumber="KTR-01" title="Susun Draf Kontrak PKS Baru">
                <form onSubmit={(e) => void handleCreateContract(e)} className="space-y-3">
                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                    <FormField id="ktr-num" label="Nomor Kontrak" required>
                      <Input
                        id="ktr-num"
                        monospace
                        placeholder="KTR-AGRO-2026-009"
                        value={contractNum}
                        onChange={(e) => setContractNum(e.target.value)}
                      />
                    </FormField>
                    <FormField id="ktr-mill" label="PKS Mitra Tujuan" required>
                      <Select
                        id="ktr-mill"
                        value={millId || mills[0]?.id || ''}
                        onChange={(e) => setMillId(e.target.value)}
                      >
                        {mills.map((m) => (
                          <option key={m.id} value={m.id}>
                            {m.mill_code} - {m.mill_name}
                          </option>
                        ))}
                      </Select>
                    </FormField>
                  </div>

                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                    <FormField id="ktr-start" label="Tanggal Mulai" required>
                      <Input
                        id="ktr-start"
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                      />
                    </FormField>
                    <FormField id="ktr-end" label="Tanggal Akhir" required>
                      <Input
                        id="ktr-end"
                        type="date"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                      />
                    </FormField>
                    <FormField id="ktr-quota" label="Kuota Awal (kg)" required>
                      <Input
                        id="ktr-quota"
                        monospace
                        value={initialQuotaKg}
                        onChange={(e) => setInitialQuotaKg(e.target.value)}
                      />
                    </FormField>
                  </div>

                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                    <FormField id="ktr-rule" label="Aturan Harga">
                      <Select
                        id="ktr-rule"
                        value={priceRuleType}
                        onChange={(e) =>
                          setPriceRuleType(
                            e.target.value as 'FIXED' | 'REFERENCE_FORMULA' | 'PERIOD_SCHEDULE',
                          )
                        }
                      >
                        <option value="FIXED">FIXED (Harga Kontrak Tetap)</option>
                        <option value="REFERENCE_FORMULA">REFERENCE_FORMULA</option>
                        <option value="PERIOD_SCHEDULE">PERIOD_SCHEDULE</option>
                      </Select>
                    </FormField>
                    <FormField id="ktr-price" label="Harga Kontrak (Rp/kg)">
                      <Input
                        id="ktr-price"
                        monospace
                        disabled={priceRuleType !== 'FIXED'}
                        value={agreedPrice}
                        onChange={(e) => setAgreedPrice(e.target.value)}
                      />
                    </FormField>
                    <FormField id="ktr-model" label="Model Usaha (Pending SOP)">
                      <Select
                        id="ktr-model"
                        value={businessModel}
                        onChange={(e) =>
                          setBusinessModel(e.target.value as 'UNCONFIRMED' | 'PRINCIPAL' | 'AGENT')
                        }
                      >
                        <option value="UNCONFIRMED">UNCONFIRMED (Pending SOP)</option>
                        <option value="PRINCIPAL">PRINCIPAL (Simulasi)</option>
                        <option value="AGENT">AGENT (Simulasi)</option>
                      </Select>
                    </FormField>
                  </div>

                  <Button
                    type="submit"
                    isLoading={createContract.isPending}
                    leadingIcon={<Plus aria-hidden="true" className="h-4 w-4" />}
                  >
                    Simpan Draf Kontrak
                  </Button>
                </form>
              </FormSection>
            </div>
          ) : null}

          {canReserve ? (
            <div className="xl:col-span-5">
              <FormSection
                stepNumber="QTA-01"
                title="Reservasi Kuota Atomik (Idempotent)"
                description="Mencegah over-allocation saat beberapa e-DO berjalan serentak (BR-KTR-002)."
              >
                <form onSubmit={(e) => void handleReserveQuota(e)} className="space-y-3">
                  <FormField id="res-ktr" label="Kontrak Aktif">
                    <Select
                      id="res-ktr"
                      value={selectedContractForQuota?.id ?? ''}
                      onChange={(e) => setReserveContractId(e.target.value)}
                    >
                      {contracts.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.contract_number} ({c.status})
                        </option>
                      ))}
                    </Select>
                  </FormField>
                  <FormField id="res-do" label="Target e-DO">
                    <Select
                      id="res-do"
                      value={reserveDoId || deliveryOrders[0]?.id || ''}
                      onChange={(e) => setReserveDoId(e.target.value)}
                    >
                      {deliveryOrders.map((d) => (
                        <option key={d.id} value={d.id}>
                          {d.delivery_order_number} ({formatKg(d.total_origin_weight_kg)})
                        </option>
                      ))}
                    </Select>
                  </FormField>
                  <FormField id="res-kg" label="Berat Dicadangkan (kg)" required>
                    <Input
                      id="res-kg"
                      monospace
                      value={reserveKg}
                      onChange={(e) => setReserveKg(e.target.value)}
                    />
                  </FormField>
                  <Button
                    type="submit"
                    variant="secondary"
                    fullWidth
                    isLoading={reserveQuota.isPending}
                    leadingIcon={<ShieldCheck aria-hidden="true" className="h-4 w-4" />}
                  >
                    Cadangkan Kuota PKS
                  </Button>
                </form>
              </FormSection>
            </div>
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

      {contractsQuery.isError ? (
        <StateFeedbackCard
          variant="error"
          error={contractsQuery.error}
          onAction={() => void contractsQuery.refetch()}
        />
      ) : (
        <DataTable<TradeContract>
          caption="Daftar Kontrak PKS & Kuota Aktif"
          rows={contracts}
          isLoading={contractsQuery.isLoading}
          getRowKey={(c) => c.id}
          columns={[
            {
              key: 'num',
              header: 'Kontrak & PKS',
              render: (c) => (
                <div>
                  <p className="font-mono text-xs font-bold text-primary-default">
                    {c.contract_number}
                  </p>
                  <p className="font-semibold text-ink-primary">{c.mill_name}</p>
                  <p className="text-xs text-text-muted">
                    {formatCalendarOrWibDate(c.start_date)} s.d. {formatCalendarOrWibDate(c.end_date)}
                  </p>
                </div>
              ),
            },
            {
              key: 'model',
              header: 'Model Usaha & Harga',
              render: (c) => (
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-1.5">
                    <StatusIndicator status={c.business_model_code} />
                    <Badge tone="warning">{c.policy_classification}</Badge>
                  </div>
                  <p className="text-xs text-ink-secondary">
                    {c.agreed_price_per_kg
                      ? formatPricePerKg(c.agreed_price_per_kg)
                      : c.price_rule_type}
                  </p>
                </div>
              ),
            },
            {
              key: 'quota',
              header: 'Kuota Tersedia / Batas',
              align: 'right',
              render: (c) => {
                const p = c.quota_periods[0];
                return p ? (
                  <div className="text-xs">
                    <p className="font-mono font-bold text-primary-default">
                      Sisa: {formatKg(p.available_quota_kg)}
                    </p>
                    <p className="text-text-muted">
                      Batas: {formatKg(p.quota_limit_kg)} | Tercadang:{' '}
                      {formatKg(p.active_reserved_kg)}
                    </p>
                  </div>
                ) : (
                  '-'
                );
              },
            },
            {
              key: 'status',
              header: 'Status Kontrak',
              render: (c) => <StatusIndicator status={c.status} />,
            },
          ]}
        />
      )}
    </DataManagementTemplate>
  );
}
