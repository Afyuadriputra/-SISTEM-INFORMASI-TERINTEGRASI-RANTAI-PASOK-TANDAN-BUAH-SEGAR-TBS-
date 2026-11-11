import { Link } from '@tanstack/react-router';
import { CheckCircle2 } from 'lucide-react';
import { PolicyNoticeBanner } from '@/components/molecules';
import { PageHeader, StateFeedbackCard } from '@/components/organisms';
import { PublicTemplate } from '@/components/templates';
import { usePublicProfile } from '../api/publicApi';

export function KemitraanPage() {
  const profileQuery = usePublicProfile();
  const profile = profileQuery.data?.data;

  return (
    <PublicTemplate>
      <div className="space-y-6">
        <PageHeader
          eyebrow="PORTAL PUBLIK | KEMITRAAN"
          title={profile?.partnership_title ?? 'Informasi Kemitraan TBS'}
          description="Panduan alur kerja sama pasokan TBS bagi koperasi tani, petani swadaya terdata, dan PKS mitra."
        />

        {profileQuery.isLoading ? (
          <StateFeedbackCard variant="loading" title="Memuat informasi kemitraan..." />
        ) : profileQuery.isError ? (
          <StateFeedbackCard
            variant="error"
            error={profileQuery.error}
            onAction={() => void profileQuery.refetch()}
          />
        ) : profile ? (
          <div className="space-y-6">
            <article className="rounded-lg border border-border-subtle bg-surface-default p-6">
              <h2 className="text-lg font-bold text-ink-primary">Ringkasan Skema Kemitraan</h2>
              <p className="mt-2 leading-relaxed text-ink-secondary">{profile.partnership_summary}</p>

              <h3 className="mt-6 text-sm font-bold uppercase tracking-wide text-primary-default">
                Persyaratan Kemitraan Awal
              </h3>
              <ul className="mt-3 space-y-2.5">
                {profile.partnership_requirements.map((req, index) => (
                  <li key={index} className="flex items-start gap-2.5 text-sm text-ink-primary">
                    <CheckCircle2
                      aria-hidden="true"
                      className="mt-0.5 h-4 w-4 shrink-0 text-primary-default"
                    />
                    <span>{req}</span>
                  </li>
                ))}
              </ul>
            </article>

            <PolicyNoticeBanner
              kind="info"
              title="Prosedur Pengajuan Kemitraan (FR-PUB-007)"
              description="Pendaftaran mitra secara otomatis tidak dilakukan melalui formulir anonim di Portal Publik demi menjaga validasi identitas. Calon koperasi atau PKS mitra dipersilakan menghubungi kontak resmi Perumda Tuah Sekata untuk verifikasi dokumen."
              footer={
                <Link to="/kontak" className="font-semibold underline">
                  Lihat Saluran Kontak Resmi
                </Link>
              }
            />
          </div>
        ) : null}
      </div>
    </PublicTemplate>
  );
}
