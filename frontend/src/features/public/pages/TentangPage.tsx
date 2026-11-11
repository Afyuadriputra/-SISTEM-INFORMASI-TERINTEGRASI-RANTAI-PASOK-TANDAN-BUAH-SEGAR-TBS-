import { LocationLink, PolicyNoticeBanner } from '@/components/molecules';
import { PageHeader, StateFeedbackCard } from '@/components/organisms';
import { PublicTemplate } from '@/components/templates';
import { usePublicProfile } from '../api/publicApi';

export function TentangPage() {
  const profileQuery = usePublicProfile();
  const profile = profileQuery.data?.data;

  return (
    <PublicTemplate>
      <div className="space-y-6">
        <PageHeader
          eyebrow="PROFIL PERUSAHAAN DAERAH"
          title={profile?.about_title ?? 'Tentang Perumda Tuah Sekata'}
          description={profile?.organization_name ?? 'Perusahaan Umum Daerah Tuah Sekata Kabupaten Pelalawan'}
        />

        {profileQuery.isLoading ? (
          <StateFeedbackCard variant="loading" title="Memuat profil perusahaan..." />
        ) : profileQuery.isError ? (
          <StateFeedbackCard
            variant="error"
            error={profileQuery.error}
            onAction={() => void profileQuery.refetch()}
          />
        ) : profile ? (
          <div className="space-y-6">
            <PolicyNoticeBanner
              kind="info"
              title={`Fokus Ruang Lingkup: ${profile.business_unit_name}`}
              description={profile.excluded_units_notice}
            />

            <article className="rounded-lg border border-border-subtle bg-surface-default p-6">
              <h2 className="text-lg font-bold text-ink-primary">Mandat Tata Niaga TBS Daerah</h2>
              <p className="mt-3 leading-relaxed text-ink-secondary">{profile.about_summary}</p>

              <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">
                <div className="rounded-md border border-border-subtle bg-surface-subtle/60 p-4">
                  <p className="text-xs font-bold uppercase text-primary-default">Transparansi</p>
                  <p className="mt-1 text-sm text-ink-primary">
                    Publikasi harga beli multi-PKS dan acuan Dinas Perkebunan yang terverifikasi.
                  </p>
                </div>
                <div className="rounded-md border border-border-subtle bg-surface-subtle/60 p-4">
                  <p className="text-xs font-bold uppercase text-primary-default">Akuntabilitas</p>
                  <p className="mt-1 text-sm text-ink-primary">
                    Jejak penerimaan kebun, e-DO, tiket timbang pabrik, rekonsiliasi susut, dan
                    pembayaran yang teraudit.
                  </p>
                </div>
                <div className="rounded-md border border-border-subtle bg-surface-subtle/60 p-4">
                  <p className="text-xs font-bold uppercase text-primary-default">Kerahasiaan</p>
                  <p className="mt-1 text-sm text-ink-primary">
                    Pemisahan tegas antara informasi publik terkurasi dengan identitas petani dan
                    kontrak bisnis internal.
                  </p>
                </div>
              </div>
            </article>

            <section className="space-y-3">
              <h2 className="text-lg font-bold text-ink-primary">Kantor Operasional Terdaftar</h2>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {profile.offices.map((office) => (
                  <div
                    key={office.id}
                    className="rounded-lg border border-border-subtle bg-surface-default p-5"
                  >
                    <h3 className="text-base font-bold text-ink-primary">{office.office_name}</h3>
                    <div className="mt-2">
                      <LocationLink
                        address={office.address}
                        latitude={office.latitude}
                        longitude={office.longitude}
                        hasVerifiedCoordinates={
                          office.latitude !== null && office.longitude !== null
                        }
                      />
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>
        ) : null}
      </div>
    </PublicTemplate>
  );
}
