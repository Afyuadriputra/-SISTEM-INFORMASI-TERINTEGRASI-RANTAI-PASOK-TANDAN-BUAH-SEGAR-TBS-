import { Link, useParams } from '@tanstack/react-router';
import { ArrowLeft, Phone } from 'lucide-react';
import { Badge } from '@/components/atoms';
import { LocationLink, PolicyNoticeBanner, PriceDisplay } from '@/components/molecules';
import { PageHeader, StateFeedbackCard } from '@/components/organisms';
import { PublicTemplate } from '@/components/templates';
import { usePublicMillDetail } from '../api/publicApi';

export function PksDetailPage() {
  const { id } = useParams({ strict: false }) as { id: string };
  const detailQuery = usePublicMillDetail(id);

  if (detailQuery.isLoading) {
    return (
      <PublicTemplate>
        <StateFeedbackCard variant="loading" title="Memuat detail profil dan harga PKS..." />
      </PublicTemplate>
    );
  }

  if (detailQuery.isError) {
    return (
      <PublicTemplate>
        <div className="space-y-4">
          <Link
            to="/harga-tbs"
            className="inline-flex min-h-[44px] items-center gap-1.5 text-sm font-semibold text-primary-default"
          >
            <ArrowLeft aria-hidden="true" className="h-4 w-4" />
            <span>Kembali ke Daftar Harga TBS</span>
          </Link>
          <StateFeedbackCard
            variant="error"
            error={detailQuery.error}
            onAction={() => void detailQuery.refetch()}
          />
        </div>
      </PublicTemplate>
    );
  }

  const detail = detailQuery.data?.data;
  if (!detail) {
    return (
      <PublicTemplate>
        <StateFeedbackCard variant="empty" title="Profil PKS Tidak Ditemukan" />
      </PublicTemplate>
    );
  }

  const { mill, latest_prices: latestPrices, privacy_notice: privacyNotice } = detail;

  return (
    <PublicTemplate>
      <div className="space-y-6">
        <Link
          to="/harga-tbs"
          className="inline-flex min-h-[44px] items-center gap-1.5 text-sm font-semibold text-primary-default hover:text-brand-hover"
        >
          <ArrowLeft aria-hidden="true" className="h-4 w-4" />
          <span>Kembali ke Perbandingan Harga</span>
        </Link>

        <PageHeader
          eyebrow={`PROFIL PKS TERPUBLIKASI | ${mill.mill_code}`}
          title={mill.mill_name}
          description={`Perusahaan Pengelola: ${mill.company_name}`}
        />

        <PolicyNoticeBanner
          kind="info"
          title="Kebijakan Informasi Publik PKS (BR-PUB-004)"
          description={privacyNotice}
        />

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
          <section className="space-y-4 rounded-lg border border-border-subtle bg-surface-default p-6 lg:col-span-5">
            <h2 className="text-base font-bold text-ink-primary">Identitas & Lokasi Resmi</h2>
            <LocationLink
              address={mill.address}
              district={mill.district}
              regency={mill.regency}
              latitude={mill.latitude}
              longitude={mill.longitude}
              hasVerifiedCoordinates={mill.has_verified_coordinates}
            />
            {mill.public_contact_phone ? (
              <div className="flex items-center gap-2 text-sm text-ink-primary">
                <Phone aria-hidden="true" className="h-4 w-4 text-primary-default" />
                <span>Kontak Resmi: {mill.public_contact_phone}</span>
              </div>
            ) : null}
          </section>

          <section className="space-y-4 rounded-lg border border-border-subtle bg-surface-default p-6 lg:col-span-7">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h2 className="text-base font-bold text-ink-primary">
                Kutipan Harga Pembelian Terkini
              </h2>
              <Badge tone="primary">{latestPrices.length} Kategori</Badge>
            </div>
            {latestPrices.length === 0 ? (
              <p className="text-sm text-ink-secondary">
                Saat ini belum ada kutipan harga aktif yang dipublikasikan untuk PKS ini.
              </p>
            ) : (
              <div className="divide-y divide-border-subtle">
                {latestPrices.map((quote) => (
                  <div key={quote.id} className="py-4 first:pt-0 last:pb-0">
                    <PriceDisplay
                      emphasis="hero"
                      pricePerKg={quote.price_per_kg}
                      categoryName={quote.price_category_name}
                      sourceName={quote.source_name}
                      updatedAt={quote.updated_at}
                      isExpired={quote.is_expired}
                      isSimulation={quote.is_simulation}
                    />
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </PublicTemplate>
  );
}
