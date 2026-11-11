import { Link } from '@tanstack/react-router';
import { Phone } from 'lucide-react';
import { LocationLink, PolicyNoticeBanner } from '@/components/molecules';
import { PageHeader, StateFeedbackCard } from '@/components/organisms';
import { PublicTemplate } from '@/components/templates';
import { usePublicProfile } from '../api/publicApi';

export function KontakPage() {
  const profileQuery = usePublicProfile();
  const profile = profileQuery.data?.data;

  return (
    <PublicTemplate>
      <div className="space-y-6">
        <PageHeader
          eyebrow="PORTAL PUBLIK | KONTAK RESMI"
          title="Kontak Resmi Unit Agro Niaga"
          description="Saluran komunikasi resmi Perumda Tuah Sekata untuk verifikasi kemitraan dan konfirmasi informasi publik."
        />

        {profileQuery.isLoading ? (
          <StateFeedbackCard variant="loading" title="Memuat kontak resmi..." />
        ) : profileQuery.isError ? (
          <StateFeedbackCard
            variant="error"
            error={profileQuery.error}
            onAction={() => void profileQuery.refetch()}
          />
        ) : profile ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {profile.offices.map((office) => (
                <article
                  key={office.id}
                  className="space-y-3 rounded-lg border border-border-subtle bg-surface-default p-6"
                >
                  <h2 className="text-lg font-bold text-ink-primary">{office.office_name}</h2>
                  <LocationLink
                    address={office.address}
                    latitude={office.latitude}
                    longitude={office.longitude}
                    hasVerifiedCoordinates={
                      office.latitude !== null && office.longitude !== null
                    }
                  />
                  {office.public_contact ? (
                    <p className="flex items-center gap-2 pl-6 text-sm font-semibold text-primary-default">
                      <Phone aria-hidden="true" className="h-4 w-4" />
                      <span>{office.public_contact}</span>
                    </p>
                  ) : null}
                </article>
              ))}
            </div>

            <PolicyNoticeBanner
              kind="info"
              title="Sudah Terdaftar sebagai Mitra atau Petugas Internal?"
              description="Petani terdaftar, operator koperasi, staf Perumda, petugas PKS, dan Direksi dapat masuk ke Portal Internal menggunakan akun yang diterbitkan Administrator Sistem."
              footer={
                <Link to="/login" className="font-semibold underline">
                  Masuk ke Portal Internal
                </Link>
              }
            />
          </div>
        ) : null}
      </div>
    </PublicTemplate>
  );
}
