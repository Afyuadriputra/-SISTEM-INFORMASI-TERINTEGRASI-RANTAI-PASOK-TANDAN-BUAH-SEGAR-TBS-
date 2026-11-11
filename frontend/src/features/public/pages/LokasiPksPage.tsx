import { Link } from '@tanstack/react-router';
import { Suspense, lazy, useMemo, useState } from 'react';
import { Badge, Select } from '@/components/atoms';
import { LocationLink, SearchField } from '@/components/molecules';
import { FilterPanel, PageHeader, StateFeedbackCard } from '@/components/organisms';
import { PublicTemplate } from '@/components/templates';
import { usePublicMills, usePublicProfile } from '../api/publicApi';
import type { MapMarkerPoint } from '../components/PksLocationMap';

const LazyPksLocationMap = lazy(() => import('../components/PksLocationMap'));

export function LokasiPksPage() {
  const [search, setSearch] = useState('');
  const [regency, setRegency] = useState('');
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const profileQuery = usePublicProfile();
  const millsQuery = usePublicMills({
    search: search.trim() || undefined,
    regency: regency.trim() || undefined,
    page_size: 20,
  });

  const offices = useMemo(() => profileQuery.data?.data.offices ?? [], [profileQuery.data]);
  const mills = useMemo(() => millsQuery.data?.data ?? [], [millsQuery.data]);

  const mapPoints = useMemo<MapMarkerPoint[]>(() => {
    const officePts: MapMarkerPoint[] = [];
    for (const office of offices) {
      if (office.latitude !== null && office.longitude !== null) {
        const lat = Number(office.latitude);
        const lon = Number(office.longitude);
        if (Number.isFinite(lat) && Number.isFinite(lon)) {
          officePts.push({
            id: `office-${office.id}`,
            label: office.office_name,
            subtitle: office.address,
            latitude: lat,
            longitude: lon,
            kind: 'office',
          });
        }
      }
    }

    const millPts: MapMarkerPoint[] = [];
    for (const mill of mills) {
      if (mill.has_verified_coordinates && mill.latitude !== null && mill.longitude !== null) {
        const lat = Number(mill.latitude);
        const lon = Number(mill.longitude);
        if (Number.isFinite(lat) && Number.isFinite(lon)) {
          millPts.push({
            id: mill.id,
            label: mill.mill_name,
            subtitle: mill.address,
            latitude: lat,
            longitude: lon,
            kind: 'mill',
          });
        }
      }
    }

    return [...officePts, ...millPts];
  }, [mills, offices]);

  return (
    <PublicTemplate>
      <div className="space-y-6">
        <PageHeader
          eyebrow="PORTAL PUBLIK | PETA & LOKASI"
          title="Lokasi Kantor Perumda & PKS Mitra"
          description="Menampilkan alamat terdaftar dan titik peta hanya untuk lokasi yang koordinatnya telah diverifikasi resmi (BR-PUB-004 / DEC-014)."
        />

        <FilterPanel
          onReset={() => {
            setSearch('');
            setRegency('');
            setSelectedId(null);
          }}
        >
          <div className="min-w-[220px] flex-1">
            <label htmlFor="loc-search" className="mb-1 block text-xs font-semibold text-ink-secondary">
              Cari PKS atau Alamat
            </label>
            <SearchField
              id="loc-search"
              value={search}
              onChange={setSearch}
              placeholder="Nama pabrik atau kecamatan..."
            />
          </div>
          <div className="min-w-[180px]">
            <label htmlFor="loc-regency" className="mb-1 block text-xs font-semibold text-ink-secondary">
              Kabupaten
            </label>
            <Select id="loc-regency" value={regency} onChange={(e) => setRegency(e.target.value)}>
              <option value="">Semua Kabupaten</option>
              <option value="Pelalawan">Pelalawan</option>
              <option value="Siak">Siak</option>
            </Select>
          </div>
        </FilterPanel>

        <Suspense fallback={<StateFeedbackCard variant="loading" title="Memuat komponen peta..." />}>
          <LazyPksLocationMap
            points={mapPoints}
            selectedId={selectedId}
            onSelectPoint={setSelectedId}
          />
        </Suspense>

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
          <section className="space-y-3 lg:col-span-5">
            <h2 className="text-lg font-bold text-ink-primary">Kantor Perumda Tuah Sekata</h2>
            {profileQuery.isLoading ? (
              <StateFeedbackCard variant="loading" />
            ) : (
              offices.map((office) => (
                <article
                  key={office.id}
                  className="rounded-lg border border-border-subtle bg-surface-default p-4"
                >
                  <div className="flex items-center justify-between gap-2">
                    <h3 className="text-sm font-bold text-ink-primary">{office.office_name}</h3>
                    <Badge tone="warning">Kantor Resmi</Badge>
                  </div>
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
                  {office.public_contact ? (
                    <p className="mt-2 pl-6 text-xs font-semibold text-ink-secondary">
                      Kontak: {office.public_contact}
                    </p>
                  ) : null}
                </article>
              ))
            )}
          </section>

          <section className="space-y-3 lg:col-span-7">
            <h2 className="text-lg font-bold text-ink-primary">Daftar PKS Mitra Terpublikasi</h2>
            {millsQuery.isLoading ? (
              <StateFeedbackCard variant="loading" />
            ) : millsQuery.isError ? (
              <StateFeedbackCard
                variant="error"
                error={millsQuery.error}
                onAction={() => void millsQuery.refetch()}
              />
            ) : mills.length === 0 ? (
              <StateFeedbackCard variant="empty" title="PKS Tidak Ditemukan" />
            ) : (
              <div className="space-y-3">
                {mills.map((mill) => (
                  <article
                    key={mill.id}
                    className={`rounded-lg border p-4 transition-colors ${
                      selectedId === mill.id
                        ? 'border-primary-default bg-primary-subtle/35'
                        : 'border-border-subtle bg-surface-default'
                    }`}
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div>
                        <p className="font-mono text-xs text-text-muted">{mill.mill_code}</p>
                        <h3 className="text-base font-bold text-ink-primary">{mill.mill_name}</h3>
                      </div>
                      <Badge tone={mill.has_verified_coordinates ? 'success' : 'neutral'}>
                        {mill.has_verified_coordinates
                          ? 'Koordinat Terverifikasi'
                          : 'Alamat Terdaftar'}
                      </Badge>
                    </div>
                    <div className="mt-2">
                      <LocationLink
                        address={mill.address}
                        district={mill.district}
                        regency={mill.regency}
                        latitude={mill.latitude}
                        longitude={mill.longitude}
                        hasVerifiedCoordinates={mill.has_verified_coordinates}
                      />
                    </div>
                    <div className="mt-3 flex flex-wrap gap-3 pl-6">
                      <Link
                        to="/pks/$id"
                        params={{ id: mill.id }}
                        className="text-xs font-semibold text-primary-default underline"
                      >
                        Lihat Harga & Profil PKS
                      </Link>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </PublicTemplate>
  );
}
