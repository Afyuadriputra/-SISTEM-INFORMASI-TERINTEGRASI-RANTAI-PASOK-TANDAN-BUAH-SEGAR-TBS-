import { Link } from '@tanstack/react-router';
import { useState } from 'react';
import { Badge, Checkbox, Select } from '@/components/atoms';
import { PaginationControl, SearchField } from '@/components/molecules';
import { DataTable, FilterPanel, PageHeader, StateFeedbackCard } from '@/components/organisms';
import { PublicTemplate } from '@/components/templates';
import {
  formatCalendarOrWibDate,
  formatPricePerKg,
  formatWibDateTime,
} from '@/lib/decimal/precision';
import {
  usePublicDisbunPrices,
  usePublicPrices,
  type PublicPriceListEnvelope,
} from '../api/publicApi';

type QuoteRow = PublicPriceListEnvelope['data'][number];

export function HargaTbsPage() {
  const [search, setSearch] = useState('');
  const [regency, setRegency] = useState('');
  const [categoryCode, setCategoryCode] = useState('');
  const [sortOption, setSortOption] = useState<'price_desc' | 'price_asc' | 'updated_desc'>(
    'price_desc',
  );
  const [includeExpired, setIncludeExpired] = useState(false);
  const [page, setPage] = useState(1);

  const sortParams =
    sortOption === 'price_asc'
      ? ({ sort_by: 'price_per_kg', sort_dir: 'asc' } as const)
      : sortOption === 'updated_desc'
        ? ({ sort_by: 'updated_at', sort_dir: 'desc' } as const)
        : ({ sort_by: 'price_per_kg', sort_dir: 'desc' } as const);

  const pricesQuery = usePublicPrices({
    search: search.trim() || undefined,
    regency: regency.trim() || undefined,
    category_code: categoryCode || undefined,
    ...sortParams,
    include_expired: includeExpired,
    page,
    page_size: 10,
  });
  const disbunQuery = usePublicDisbunPrices();

  const quotes = pricesQuery.data?.data ?? [];
  const meta = pricesQuery.data?.meta;
  const disbunList = disbunQuery.data?.data ?? [];

  const handleReset = () => {
    setSearch('');
    setRegency('');
    setCategoryCode('');
    setSortOption('price_desc');
    setIncludeExpired(false);
    setPage(1);
  };

  return (
    <PublicTemplate>
      <div className="space-y-6">
        <PageHeader
          eyebrow="PORTAL PUBLIK | HARGA TBS"
          title="Perbandingan Harga TBS Multi-PKS"
          description="Bandingkan penawaran harga pembelian TBS antar PKS mitra yang telah diverifikasi dan dipublikasikan, lengkap dengan periode berlaku dan acuan resmi Disbun secara terpisah."
        />

        <section
          aria-label="Harga Acuan Resmi Dinas Perkebunan"
          className="rounded-lg border border-primary-default/25 bg-primary-subtle/50 p-4"
        >
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <h2 className="text-sm font-bold text-primary-default">
                Referensi Resmi Dinas Perkebunan (Disbun)
              </h2>
              <p className="text-xs text-ink-secondary">
                Sumber resmi pemerintah daerah dipisahkan dari daftar harga penawaran PKS swasta
                (BR-004).
              </p>
            </div>
            <Badge tone="primary">Kategori Acuan Resmi</Badge>
          </div>
          {disbunList.length > 0 ? (
            <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {disbunList.map((d) => (
                <div
                  key={d.id}
                  className="rounded-md border border-border-subtle bg-surface-default px-4 py-3"
                >
                  <p className="font-mono text-xl font-bold text-primary-default tabular-nums">
                    {formatPricePerKg(d.price_per_kg)}
                  </p>
                  <p className="mt-1 text-xs font-semibold text-ink-primary">
                    {d.category_name} ({d.age_group ?? '-'})
                  </p>
                  <p className="text-xs text-text-muted">
                    {d.source_name} | Berlaku {formatCalendarOrWibDate(d.effective_from)}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="mt-2 text-xs text-ink-secondary">
              Belum ada harga acuan Disbun yang aktif pada periode ini.
            </p>
          )}
        </section>

        <FilterPanel onReset={handleReset}>
          <div className="min-w-[220px] flex-1">
            <label htmlFor="price-search" className="mb-1 block text-xs font-semibold text-ink-secondary">
              Cari PKS / Kode
            </label>
            <SearchField
              id="price-search"
              value={search}
              onChange={(val) => {
                setSearch(val);
                setPage(1);
              }}
              placeholder="Contoh: Pangkalan Kerinci atau PKS-PKC-01"
            />
          </div>

          <div className="min-w-[160px]">
            <label htmlFor="filter-regency" className="mb-1 block text-xs font-semibold text-ink-secondary">
              Kabupaten
            </label>
            <Select
              id="filter-regency"
              value={regency}
              onChange={(e) => {
                setRegency(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Semua Kabupaten</option>
              <option value="Pelalawan">Pelalawan</option>
              <option value="Siak">Siak</option>
              <option value="Kampar">Kampar</option>
            </Select>
          </div>

          <div className="min-w-[180px]">
            <label htmlFor="filter-category" className="mb-1 block text-xs font-semibold text-ink-secondary">
              Kategori Kualitas
            </label>
            <Select
              id="filter-category"
              value={categoryCode}
              onChange={(e) => {
                setCategoryCode(e.target.value);
                setPage(1);
              }}
            >
              <option value="">Semua Kategori</option>
              <option value="TBS_PLASMA">TBS Plasma</option>
              <option value="TBS_SWADAYA">TBS Swadaya</option>
            </Select>
          </div>

          <div className="min-w-[190px]">
            <label htmlFor="filter-sort" className="mb-1 block text-xs font-semibold text-ink-secondary">
              Urutkan
            </label>
            <Select
              id="filter-sort"
              value={sortOption}
              onChange={(e) => {
                setSortOption(e.target.value as typeof sortOption);
                setPage(1);
              }}
            >
              <option value="price_desc">Harga Tertinggi ke Terendah</option>
              <option value="price_asc">Harga Terendah ke Tertinggi</option>
              <option value="updated_desc">Pembaruan Terbaru</option>
            </Select>
          </div>

          <div className="pt-2">
            <Checkbox
              id="include-expired-toggle"
              label="Sertakan harga kedaluwarsa"
              checked={includeExpired}
              onChange={(e) => {
                setIncludeExpired(e.target.checked);
                setPage(1);
              }}
            />
          </div>
        </FilterPanel>

        <p className="text-xs text-ink-secondary">
          Catatan perbandingan (BR-PRC-011): Pastikan membandingkan harga pada kategori mutu yang
          setara (misalnya sesama TBS Swadaya atau sesama TBS Plasma).
        </p>

        {pricesQuery.isLoading ? (
          <StateFeedbackCard variant="loading" title="Memuat perbandingan harga TBS..." />
        ) : pricesQuery.isError ? (
          <StateFeedbackCard
            variant="error"
            error={pricesQuery.error}
            onAction={() => void pricesQuery.refetch()}
          />
        ) : (
          <div className="space-y-4">
            <DataTable<QuoteRow>
              caption="Daftar Harga Pembelian TBS Multi-PKS Terpublikasi"
              rows={quotes}
              getRowKey={(row) => row.id}
              emptyTitle="Tidak Ada Harga PKS yang Cocok"
              emptyDescription="Tidak ditemukan kutipan harga terpublikasi sesuai filter saat ini."
              columns={[
                {
                  key: 'mill',
                  header: 'PKS Mitra',
                  render: (row) => (
                    <div className="space-y-0.5">
                      <Link
                        to="/pks/$id"
                        params={{ id: row.mill_id }}
                        className="font-bold text-primary-default hover:underline"
                      >
                        {row.mill_name}
                      </Link>
                      <p className="font-mono text-xs text-text-muted">
                        {row.mill_code} | {row.regency}
                      </p>
                    </div>
                  ),
                },
                {
                  key: 'category',
                  header: 'Kategori & Sumber',
                  render: (row) => (
                    <div className="space-y-0.5">
                      <p className="font-semibold text-ink-primary">{row.price_category_name}</p>
                      <p className="text-xs text-ink-secondary">{row.source_name}</p>
                    </div>
                  ),
                },
                {
                  key: 'price',
                  header: 'Harga',
                  align: 'right',
                  render: (row) => (
                    <div className="space-y-1">
                      <p className="font-mono text-base font-bold text-primary-default">
                        {formatPricePerKg(row.price_per_kg)}
                      </p>
                      <div className="flex flex-wrap justify-end gap-1">
                        {row.is_expired ? <Badge tone="warning">Kedaluwarsa</Badge> : null}
                        {row.is_simulation ? <Badge tone="warning">Simulasi</Badge> : null}
                      </div>
                    </div>
                  ),
                },
                {
                  key: 'period',
                  header: 'Periode & Pembaruan',
                  render: (row) => (
                    <div className="space-y-0.5 text-xs">
                      <p className="text-ink-primary">
                        Berlaku: {formatWibDateTime(row.effective_from)}
                      </p>
                      <p className="text-text-muted">
                        Diperbarui: {formatWibDateTime(row.updated_at)}
                      </p>
                    </div>
                  ),
                },
              ]}
            />

            {meta ? (
              <PaginationControl
                page={meta.page}
                totalPages={meta.total_pages}
                totalItems={meta.total_items}
                pageSize={meta.page_size}
                hasPrev={meta.has_prev}
                hasNext={meta.has_next}
                onPageChange={setPage}
              />
            ) : null}
          </div>
        )}
      </div>
    </PublicTemplate>
  );
}
