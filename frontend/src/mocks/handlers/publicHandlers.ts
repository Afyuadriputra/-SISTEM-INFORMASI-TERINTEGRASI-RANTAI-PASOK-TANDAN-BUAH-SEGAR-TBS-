import { http } from 'msw';
import type { components } from '@/lib/api/generated';
import { mockDb } from '../mockDb';
import { makeErrorResponse, makePaginatedEnvelope, makeSimpleEnvelope } from '../utils';

type PublicPriceQuote = components['schemas']['PublicPriceQuote'];
type PublicMillSummary = components['schemas']['PublicMillSummary'];

function buildPublicPriceQuotes(): PublicPriceQuote[] {
  const now = Date.now();
  return mockDb.millPriceQuotes
    .filter((q) => q.status === 'PUBLISHED')
    .map((q) => {
      const expired = q.effective_until ? new Date(q.effective_until).getTime() < now : false;
      return {
        id: q.id,
        mill_id: q.mill_id,
        mill_name: q.mill_name,
        mill_code: q.mill_code ?? '',
        regency: q.regency ?? '',
        price_category_code: q.price_category_code ?? '',
        price_category_name: q.price_category_name ?? '',
        unit: q.unit ?? 'IDR/kg',
        source_name: q.source_name ?? '',
        source_type: (q.source_type ?? 'VERIFIED_MANUAL') as PublicPriceQuote['source_type'],
        price_per_kg: q.price_per_kg,
        effective_from: q.effective_from,
        effective_until: q.effective_until,
        status: 'PUBLISHED' as const,
        display_status: expired ? 'EXPIRED' : 'PUBLISHED',
        is_expired: expired,
        updated_at: q.updated_at,
        published_at: q.published_at ?? q.updated_at,
        is_simulation: q.is_simulation ?? true,
      };
    });
}

function buildPublicMillSummaries(): PublicMillSummary[] {
  const quotes = buildPublicPriceQuotes();
  return mockDb.mills
    .filter((m) => m.is_public)
    .map((m) => {
      const millQuotes = quotes.filter((q) => q.mill_id === m.id && !q.is_expired);
      const topQuote = millQuotes[0] ?? null;
      return {
        id: m.id,
        mill_code: m.mill_code,
        mill_name: m.mill_name,
        company_name: m.company_name,
        address: m.address,
        district: m.district,
        regency: m.regency,
        province: m.province,
        latitude: m.has_verified_coordinates ? m.latitude : null,
        longitude: m.has_verified_coordinates ? m.longitude : null,
        has_verified_coordinates: m.has_verified_coordinates,
        public_contact_phone: m.contact_phone,
        active_public_price_per_kg: topQuote?.price_per_kg ?? null,
        active_price_category: topQuote?.price_category_name ?? null,
        active_price_updated_at: topQuote?.updated_at ?? null,
      };
    });
}

export const publicHandlers = [
  http.get('/health/live', () => {
    return makeSimpleEnvelope({
      status: 'ok' as const,
      service: 'agroniaga-tbs-api',
      checked_at: new Date().toISOString(),
      dependencies: null,
    });
  }),

  http.get('/health/ready', () => {
    return makeSimpleEnvelope({
      status: 'ok' as const,
      service: 'agroniaga-tbs-api',
      checked_at: new Date().toISOString(),
      dependencies: {
        postgresql: 'up' as const,
        redis: 'up' as const,
      },
    });
  }),

  http.get('/api/v1/public/prices', ({ request }) => {
    const url = new URL(request.url);
    const search = (url.searchParams.get('q') ?? url.searchParams.get('search') ?? '').trim().toLowerCase();
    const regency = (url.searchParams.get('regency') ?? '').trim().toLowerCase();
    const categoryCode = (url.searchParams.get('category_code') ?? '').trim().toLowerCase();
    const sortBy = url.searchParams.get('sort_by') ?? 'price_per_kg';
    const sortDir = url.searchParams.get('sort_dir') ?? 'desc';
    const includeExpired = url.searchParams.get('include_expired') === 'true';

    let items = buildPublicPriceQuotes();
    if (!includeExpired) {
      items = items.filter((item) => !item.is_expired);
    }
    if (search) {
      items = items.filter(
        (item) =>
          item.mill_name.toLowerCase().includes(search) ||
          item.mill_code.toLowerCase().includes(search) ||
          item.regency.toLowerCase().includes(search),
      );
    }
    if (regency) {
      items = items.filter((item) => item.regency.toLowerCase().includes(regency));
    }
    if (categoryCode) {
      items = items.filter((item) => item.price_category_code.toLowerCase() === categoryCode);
    }

    items = [...items].sort((a, b) => {
      if (sortBy === 'updated_at' || sortBy === 'updated_desc') {
        const diff = new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime();
        return sortDir === 'asc' && sortBy === 'updated_at' ? diff : -diff;
      }
      if (sortBy === 'mill_name') {
        const cmp = a.mill_name.localeCompare(b.mill_name);
        return sortDir === 'desc' ? -cmp : cmp;
      }
      if (sortBy === 'price_asc') {
        return Number(a.price_per_kg) - Number(b.price_per_kg);
      }
      const diff = Number(a.price_per_kg) - Number(b.price_per_kg);
      return sortDir === 'asc' ? diff : -diff;
    });

    return makePaginatedEnvelope(items, url);
  }),

  http.get('/api/v1/public/prices/:priceQuoteId', ({ params }) => {
    const id = String(params.priceQuoteId);
    const quotes = buildPublicPriceQuotes();
    const quote = quotes.find((q) => q.id === id);
    if (!quote) {
      return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    }
    const historicalTrend = quotes
      .filter((q) => q.mill_id === quote.mill_id && q.price_category_code === quote.price_category_code)
      .map((q) => ({
        effective_from: q.effective_from,
        price_per_kg: q.price_per_kg,
        status: q.display_status,
      }));
    return makeSimpleEnvelope({ quote, historical_trend: historicalTrend });
  }),

  http.get('/api/v1/public/disbun-prices', ({ request }) => {
    const url = new URL(request.url);
    return makePaginatedEnvelope(mockDb.disbunReferencePrices, url);
  }),

  http.get('/api/v1/public/mills', ({ request }) => {
    const url = new URL(request.url);
    const search = (url.searchParams.get('q') ?? url.searchParams.get('search') ?? '').trim().toLowerCase();
    const regency = (url.searchParams.get('regency') ?? '').trim().toLowerCase();
    let mills = buildPublicMillSummaries();
    if (search) {
      mills = mills.filter(
        (m) =>
          m.mill_name.toLowerCase().includes(search) ||
          m.address.toLowerCase().includes(search) ||
          m.mill_code.toLowerCase().includes(search),
      );
    }
    if (regency) {
      mills = mills.filter((m) => m.regency.toLowerCase().includes(regency));
    }
    return makePaginatedEnvelope(mills, url);
  }),

  http.get('/api/v1/public/mills/:millId', ({ params }) => {
    const millId = String(params.millId);
    const mill = buildPublicMillSummaries().find((m) => m.id === millId);
    if (!mill) {
      return makeErrorResponse('SYS_RESOURCE_NOT_FOUND');
    }
    const latestPrices = buildPublicPriceQuotes().filter((q) => q.mill_id === mill.id);
    return makeSimpleEnvelope({
      mill,
      latest_prices: latestPrices,
      privacy_notice:
        'Hanya informasi perusahaan yang disetujui untuk publikasi yang ditampilkan di Portal Publik (BR-PUB-004).',
    });
  }),

  http.get('/api/v1/public/profile', () => {
    return makeSimpleEnvelope(mockDb.publicProfile);
  }),

  http.get('/api/v1/public/notices', ({ request }) => {
    return makePaginatedEnvelope(mockDb.publicNotices, new URL(request.url));
  }),
];
