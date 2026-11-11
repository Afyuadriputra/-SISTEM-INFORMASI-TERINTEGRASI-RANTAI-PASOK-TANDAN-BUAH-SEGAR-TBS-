import { ExternalLink, MapPin } from 'lucide-react';

export interface LocationLinkProps {
  readonly address: string;
  readonly district?: string | null;
  readonly regency?: string | null;
  readonly latitude: string | null;
  readonly longitude: string | null;
  readonly hasVerifiedCoordinates: boolean;
}

export function LocationLink({
  address,
  district,
  regency,
  latitude,
  longitude,
  hasVerifiedCoordinates,
}: LocationLinkProps) {
  const regionSuffix = [district, regency].filter(Boolean).join(', ');
  const fullAddress = regionSuffix ? `${address}, ${regionSuffix}` : address;
  const hasCoords = hasVerifiedCoordinates && latitude !== null && longitude !== null;
  const mapUrl = hasCoords
    ? `https://www.openstreetmap.org/?mlat=${encodeURIComponent(latitude)}&mlon=${encodeURIComponent(longitude)}#map=14/${encodeURIComponent(latitude)}/${encodeURIComponent(longitude)}`
    : null;

  return (
    <div className="space-y-1.5 text-sm">
      <div className="flex items-start gap-2 text-ink-primary">
        <MapPin aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0 text-primary-default" />
        <span>{fullAddress}</span>
      </div>
      {hasCoords && mapUrl ? (
        <div className="flex flex-wrap items-center gap-3 pl-6">
          <span className="font-mono text-xs text-text-muted tabular-nums">
            Koordinat: {latitude}, {longitude}
          </span>
          <a
            href={mapUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex min-h-[36px] items-center gap-1 text-xs font-semibold text-primary-default underline hover:text-brand-hover"
          >
            <span>Buka Navigasi Peta</span>
            <ExternalLink aria-hidden="true" className="h-3.5 w-3.5" />
          </a>
        </div>
      ) : (
        <p className="pl-6 text-xs text-text-muted">
          Koordinat peta belum terverifikasi. Menampilkan alamat terdaftar tanpa pin perkiraan.
        </p>
      )}
    </div>
  );
}
