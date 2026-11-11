import { Link } from '@tanstack/react-router';
import { ArrowRight, MapPin, ShieldCheck, TrendingUp } from 'lucide-react';
import { Badge } from '@/components/atoms';
import { LocationLink, PriceDisplay } from '@/components/molecules';
import { StateFeedbackCard } from '@/components/organisms';
import { PublicTemplate } from '@/components/templates';
import { formatCalendarOrWibDate, formatPricePerKg, formatWibDateTime } from '@/lib/decimal/precision';
import {
  usePublicDisbunPrices,
  usePublicMills,
  usePublicNotices,
  usePublicPrices,
} from '../api/publicApi';

export function HomePage() {
  const pricesQuery = usePublicPrices({ sort_by: 'price_per_kg', sort_dir: 'desc', page_size: 5 });
  const disbunQuery = usePublicDisbunPrices();
  const millsQuery = usePublicMills({ page_size: 3 });
  const noticesQuery = usePublicNotices();

  const prices = pricesQuery.data?.data ?? [];
  const disbunTop = disbunQuery.data?.data?.[0] ?? null;
  const mills = millsQuery.data?.data ?? [];
  const notices = noticesQuery.data?.data ?? [];

  return (
    <PublicTemplate
      fullBleedTop={
        <section className="border-b border-border-subtle bg-surface-default">
          <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:py-14">
            <div className="grid grid-cols-1 gap-8 lg:grid-cols-12 lg:items-center">
              <div className="space-y-4 lg:col-span-7">
                <p className="font-mono text-xs font-semibold uppercase tracking-wide text-primary-default">
                  PERUMDA TUAH SEKATA | UNIT AGRO NIAGA TBS
                </p>
                <h1 className="text-3xl font-bold tracking-tight text-ink-primary sm:text-4xl">
                  Transparansi Harga TBS Multi-PKS dan Rantai Pasok Terintegrasi
                </h1>
                <p className="max-w-2xl text-base leading-relaxed text-ink-secondary">
                  Pantau kutipan harga pembelian Tandan Buah Segar (TBS) yang telah diverifikasi
                  bersama acuan resmi Dinas Perkebunan serta informasi lokasi PKS mitra Kabupaten
                  Pelalawan.
                </p>
                <div className="flex flex-wrap gap-3 pt-2">
                  <Link
                    to="/harga-tbs"
                    className="inline-flex min-h-[44px] items-center gap-2 rounded-md bg-primary-default px-5 text-sm font-semibold text-primary-foreground hover:bg-brand-hover"
                  >
                    <TrendingUp aria-hidden="true" className="h-4 w-4" />
                    <span>Bandingkan Harga TBS</span>
                  </Link>
                  <Link
                    to="/lokasi-pks"
                    className="inline-flex min-h-[44px] items-center gap-2 rounded-md border border-border-control bg-surface-default px-5 text-sm font-semibold text-ink-primary hover:bg-surface-subtle"
                  >
                    <MapPin aria-hidden="true" className="h-4 w-4 text-primary-default" />
                    <span>Peta Lokasi PKS</span>
                  </Link>
                </div>
              </div>

              <div className="lg:col-span-5">
                <div className="rounded-lg border border-border-subtle bg-primary-subtle/70 p-5">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-bold uppercase tracking-wide text-primary-default">
                      Harga Acuan Resmi Disbun
                    </span>
                    <Badge tone="primary">Pembanding Resmi (BR-004)</Badge>
                  </div>
                  {disbunQuery.isLoading ? (
                    <p className="mt-3 text-sm text-ink-secondary">Memuat harga acuan Disbun...</p>
                  ) : disbunTop ? (
                    <div className="mt-3 space-y-2">
                      <p className="font-mono text-3xl font-bold text-primary-default tabular-nums">
                        {formatPricePerKg(disbunTop.price_per_kg)}
                      </p>
                      <p className="text-sm font-semibold text-ink-primary">
                        {disbunTop.category_name} ({disbunTop.age_group ?? 'Umur Produktif'})
                      </p>
                      <p className="text-xs text-ink-secondary">
                        Sumber: {disbunTop.source_name} | Berlaku{' '}
                        {formatCalendarOrWibDate(disbunTop.effective_from)}
                        {disbunTop.effective_until
                          ? ` s.d. ${formatCalendarOrWibDate(disbunTop.effective_until)}`
                          : ''}
                      </p>
                      <p className="pt-1 text-xs text-text-muted">
                        Ditampilkan terpisah dari daftar peringkat penawaran PKS swasta sesuai
                        aturan tata kelola.
                      </p>
                    </div>
                  ) : (
                    <p className="mt-3 text-sm text-ink-secondary">
                      Harga acuan Disbun periode aktif belum dipublikasikan.
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>
      }
    >
      <div className="space-y-10">
        {notices.length > 0 ? (
          <section aria-label="Pengumuman Publik" className="space-y-3">
            {notices.map((notice) => (
              <div
                key={notice.id}
                className="rounded-lg border border-primary-default/25 bg-primary-subtle/50 px-4 py-3 text-sm"
              >
                <p className="font-bold text-primary-default">{notice.title}</p>
                <p className="mt-0.5 text-ink-primary">{notice.body}</p>
              </div>
            ))}
          </section>
        ) : null}

        <section aria-labelledby="section-harga-pks" className="space-y-4">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 id="section-harga-pks" className="text-xl font-bold text-ink-primary">
                Ringkasan Harga Pembelian PKS Terverifikasi
              </h2>
              <p className="text-sm text-ink-secondary">
                Hanya harga berstatus dipublikasikan dan masih berlaku yang ditampilkan di portal
                publik.
              </p>
            </div>
            <Link
              to="/harga-tbs"
              className="inline-flex min-h-[44px] items-center gap-1.5 text-sm font-semibold text-primary-default hover:text-brand-hover"
            >
              <span>Lihat Semua & Filter</span>
              <ArrowRight aria-hidden="true" className="h-4 w-4" />
            </Link>
          </div>

          {pricesQuery.isLoading ? (
            <StateFeedbackCard variant="loading" title="Memuat daftar harga TBS multi-PKS..." />
          ) : pricesQuery.isError ? (
            <StateFeedbackCard
              variant="error"
              error={pricesQuery.error}
              onAction={() => void pricesQuery.refetch()}
            />
          ) : prices.length === 0 ? (
            <StateFeedbackCard
              variant="empty"
              title="Belum Ada Harga PKS Aktif"
              description="Saat ini belum terdapat kutipan harga PKS terpublikasi pada periode berlaku."
            />
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {prices.map((item) => (
                <article
                  key={item.id}
                  className="flex flex-col justify-between rounded-lg border border-border-subtle bg-surface-default p-5"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p className="font-mono text-xs font-semibold text-primary-default">
                          {item.mill_code}
                        </p>
                        <h3 className="text-base font-bold text-ink-primary">{item.mill_name}</h3>
                        <p className="text-xs text-ink-secondary">{item.regency}</p>
                      </div>
                    </div>
                    <PriceDisplay
                      pricePerKg={item.price_per_kg}
                      categoryName={item.price_category_name}
                      sourceName={item.source_name}
                      updatedAt={item.updated_at}
                      isExpired={item.is_expired}
                      isSimulation={item.is_simulation}
                    />
                  </div>
                  <div className="mt-4 border-t border-border-subtle pt-3">
                    <Link
                      to="/pks/$id"
                      params={{ id: item.mill_id }}
                      className="inline-flex min-h-[44px] items-center gap-1 text-xs font-semibold text-primary-default hover:text-brand-hover"
                    >
                      <span>Detail Profil & Riwayat Harga PKS</span>
                      <ArrowRight aria-hidden="true" className="h-3.5 w-3.5" />
                    </Link>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        <section aria-labelledby="section-pks-mitra" className="space-y-4">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <h2 id="section-pks-mitra" className="text-xl font-bold text-ink-primary">
                Direktori PKS Mitra Terpublikasi
              </h2>
              <p className="text-sm text-ink-secondary">
                Menampilkan lokasi pabrik dan kontak publik resmi yang disetujui untuk publikasi.
              </p>
            </div>
            <Link
              to="/lokasi-pks"
              className="inline-flex min-h-[44px] items-center gap-1.5 text-sm font-semibold text-primary-default hover:text-brand-hover"
            >
              <span>Buka Peta Lengkap</span>
              <ArrowRight aria-hidden="true" className="h-4 w-4" />
            </Link>
          </div>

          {millsQuery.isLoading ? (
            <StateFeedbackCard variant="loading" title="Memuat direktori PKS mitra..." />
          ) : millsQuery.isError ? (
            <StateFeedbackCard
              variant="error"
              error={millsQuery.error}
              onAction={() => void millsQuery.refetch()}
            />
          ) : (
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
              {mills.map((mill) => (
                <article
                  key={mill.id}
                  className="rounded-lg border border-border-subtle bg-surface-default p-5"
                >
                  <p className="font-mono text-xs text-text-muted">{mill.mill_code}</p>
                  <h3 className="mt-0.5 text-base font-bold text-ink-primary">{mill.mill_name}</h3>
                  <p className="text-xs text-ink-secondary">{mill.company_name}</p>
                  <div className="mt-3">
                    <LocationLink
                      address={mill.address}
                      district={mill.district}
                      regency={mill.regency}
                      latitude={mill.latitude}
                      longitude={mill.longitude}
                      hasVerifiedCoordinates={mill.has_verified_coordinates}
                    />
                  </div>
                  {mill.active_public_price_per_kg ? (
                    <p className="mt-3 text-xs font-semibold text-primary-default">
                      Harga Aktif: {formatPricePerKg(mill.active_public_price_per_kg)} (
                      {mill.active_price_updated_at
                        ? formatWibDateTime(mill.active_price_updated_at)
                        : 'Terbaru'}
                      )
                    </p>
                  ) : null}
                  <div className="mt-4">
                    <Link
                      to="/pks/$id"
                      params={{ id: mill.id }}
                      className="inline-flex min-h-[44px] items-center text-xs font-semibold text-primary-default underline"
                    >
                      Lihat Detail PKS
                    </Link>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>

        <section className="rounded-lg border border-border-subtle bg-surface-default p-5">
          <div className="flex items-start gap-3">
            <ShieldCheck aria-hidden="true" className="mt-0.5 h-5 w-5 shrink-0 text-primary-default" />
            <div className="space-y-1 text-xs leading-relaxed text-ink-secondary">
              <p className="text-sm font-bold text-ink-primary">
                Batasan Privasi & Ruang Lingkup Portal Publik
              </p>
              <p>
                Sesuai kebijakan keamanan dan tata kelola data (BR-PUB-001 hingga BR-PUB-005),
                portal publik bebas akses tanpa login ini hanya memuat informasi harga TBS terverifikasi,
                acuan resmi Disbun, profil Perumda Unit Agro Niaga, dan alamat PKS terpublikasi.
                Data pribadi petani, detail kontrak, rekening bank, dan e-DO hanya dapat diakses pada
                Portal Internal sesuai peran.
              </p>
            </div>
          </div>
        </section>
      </div>
    </PublicTemplate>
  );
}
