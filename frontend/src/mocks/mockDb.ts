import actorsFixture from '@contracts-fixtures/actors.json';
import contractsQuotaFixture from '@contracts-fixtures/contracts-quota.json';
import deliveryOrdersFixture from '@contracts-fixtures/delivery-orders.json';
import invoicesPaymentsFixture from '@contracts-fixtures/invoices-payments.json';
import masterDataFixture from '@contracts-fixtures/master-data.json';
import millTicketsFixture from '@contracts-fixtures/mill-tickets.json';
import millsFixture from '@contracts-fixtures/mills.json';
import publicPricesFixture from '@contracts-fixtures/public-prices.json';
import reconciliationsFixture from '@contracts-fixtures/reconciliations.json';
import tbsReceiptsFixture from '@contracts-fixtures/tbs-receipts.json';
import type { components } from '@/lib/api/generated';
import type { AuthenticatedUser } from '@/lib/auth/permissions';

/**
 * Non-production MSW simulation password shared across fixture actors during mock sessions only.
 */
export const MOCK_SIMULATION_PASSWORD = 'Simulasi123!';

export interface MockIdempotencyRecord {
  readonly payloadSignature: string;
  readonly status: number;
  readonly body: unknown;
}

export interface MockDbState {
  csrfToken: string;
  currentUserId: string | null;
  users: AuthenticatedUser[];
  parties: typeof actorsFixture.parties;
  cooperatives: components['schemas']['Cooperative'][];
  farmers: components['schemas']['Farmer'][];
  farms: components['schemas']['Farm'][];
  vehicles: components['schemas']['Vehicle'][];
  drivers: components['schemas']['Driver'][];
  millCompanies: components['schemas']['MillCompany'][];
  mills: components['schemas']['Mill'][];
  publicProfile: typeof millsFixture.public_profile;
  publicNotices: typeof millsFixture.public_notices;
  priceSources: components['schemas']['PriceSource'][];
  priceCategories: components['schemas']['PriceCategory'][];
  millPriceQuotes: components['schemas']['InternalPriceQuote'][];
  disbunReferencePrices: components['schemas']['PublicDisbunPrice'][];
  tbsReceipts: components['schemas']['TbsReceipt'][];
  tradeContracts: components['schemas']['TradeContract'][];
  quotaReservations: components['schemas']['QuotaReservation'][];
  deliveryOrders: components['schemas']['DeliveryOrder'][];
  millWeighingTickets: components['schemas']['MillWeighingTicket'][];
  systemRuleVersions: components['schemas']['SystemRuleVersion'][];
  reconciliationCases: components['schemas']['ReconciliationCase'][];
  fileAssets: components['schemas']['FileAsset'][];
  invoices: components['schemas']['Invoice'][];
  auditEvents: Array<{
    id: string;
    actor_user_id: string | null;
    actor_username: string;
    action: string;
    entity_type: string;
    entity_id: string | null;
    request_id: string;
    summary: string;
    created_at: string;
  }>;
  idempotencyStore: Map<string, MockIdempotencyRecord>;
}

function buildInitialMockDb(): MockDbState {
  const users = structuredClone(actorsFixture.authenticated_users) as AuthenticatedUser[];
  const futureEndIso = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString();
  const millPriceQuotes = structuredClone(publicPricesFixture.mill_price_quotes).map((q) => {
    if (!q.is_expired && q.effective_until && Date.parse(q.effective_until) < Date.now()) {
      return { ...q, effective_until: futureEndIso };
    }
    return q;
  });
  const disbunReferencePrices = structuredClone(publicPricesFixture.disbun_reference_prices).map(
    (d) => {
      if (d.effective_until && Date.parse(d.effective_until) < Date.now()) {
        return { ...d, effective_until: futureEndIso };
      }
      return d;
    },
  );
  return {
    csrfToken: 'csrf-sim-agroniaga-token',
    currentUserId: null,
    users,
    parties: structuredClone(actorsFixture.parties),
    cooperatives: structuredClone(
      masterDataFixture.cooperatives,
    ) as unknown as components['schemas']['Cooperative'][],
    farmers: structuredClone(
      masterDataFixture.farmers,
    ) as unknown as components['schemas']['Farmer'][],
    farms: structuredClone(masterDataFixture.farms) as unknown as components['schemas']['Farm'][],
    vehicles: structuredClone(
      masterDataFixture.vehicles,
    ) as unknown as components['schemas']['Vehicle'][],
    drivers: structuredClone(
      masterDataFixture.drivers,
    ) as unknown as components['schemas']['Driver'][],
    millCompanies: structuredClone(
      millsFixture.mill_companies,
    ) as unknown as components['schemas']['MillCompany'][],
    mills: structuredClone(millsFixture.mills) as unknown as components['schemas']['Mill'][],
    publicProfile: structuredClone(millsFixture.public_profile),
    publicNotices: structuredClone(millsFixture.public_notices),
    priceSources: structuredClone(
      publicPricesFixture.price_sources,
    ) as unknown as components['schemas']['PriceSource'][],
    priceCategories: structuredClone(
      publicPricesFixture.price_categories,
    ) as unknown as components['schemas']['PriceCategory'][],
    millPriceQuotes: millPriceQuotes as unknown as components['schemas']['InternalPriceQuote'][],
    disbunReferencePrices:
      disbunReferencePrices as unknown as components['schemas']['PublicDisbunPrice'][],
    tbsReceipts: structuredClone(
      tbsReceiptsFixture.tbs_receipts,
    ) as unknown as components['schemas']['TbsReceipt'][],
    tradeContracts: structuredClone(
      contractsQuotaFixture.trade_contracts,
    ) as unknown as components['schemas']['TradeContract'][],
    quotaReservations: structuredClone(
      contractsQuotaFixture.quota_reservations,
    ) as unknown as components['schemas']['QuotaReservation'][],
    deliveryOrders: structuredClone(
      deliveryOrdersFixture.delivery_orders,
    ) as unknown as components['schemas']['DeliveryOrder'][],
    millWeighingTickets: structuredClone(
      millTicketsFixture.mill_weighing_tickets,
    ) as unknown as components['schemas']['MillWeighingTicket'][],
    systemRuleVersions: structuredClone(
      reconciliationsFixture.system_rule_versions,
    ) as unknown as components['schemas']['SystemRuleVersion'][],
    reconciliationCases: structuredClone(
      reconciliationsFixture.reconciliation_cases,
    ) as unknown as components['schemas']['ReconciliationCase'][],
    fileAssets: structuredClone(
      invoicesPaymentsFixture.file_assets,
    ) as unknown as components['schemas']['FileAsset'][],
    invoices: structuredClone(
      invoicesPaymentsFixture.invoices,
    ) as unknown as components['schemas']['Invoice'][],
    auditEvents: [
      {
        id: 'aud-seed-001',
        actor_user_id: '10000000-0000-4000-8000-000000000005',
        actor_username: 'sim_perumda_ops_01',
        action: 'PRICE_PUBLISHED',
        entity_type: 'mill_price_quotes',
        entity_id: publicPricesFixture.mill_price_quotes[0]?.id ?? null,
        request_id: 'req-seed-001',
        summary: 'Publikasi harga referensi awal (Data Simulasi)',
        created_at: '2026-11-10T01:30:00Z',
      },
    ],
    idempotencyStore: new Map<string, MockIdempotencyRecord>(),
  };
}

export let mockDb: MockDbState = buildInitialMockDb();

export function resetMockDb(): void {
  mockDb = buildInitialMockDb();
}
