import 'maplibre-gl/dist/maplibre-gl.css';
import { useEffect, useRef, useState } from 'react';

export interface MapMarkerPoint {
  readonly id: string;
  readonly label: string;
  readonly subtitle: string;
  readonly latitude: number;
  readonly longitude: number;
  readonly kind: 'office' | 'mill';
}

export interface PksLocationMapProps {
  readonly points: readonly MapMarkerPoint[];
  readonly selectedId: string | null;
  readonly onSelectPoint: (id: string) => void;
}

interface MinimalMapHandle {
  flyTo: (opts: { center: [number, number]; zoom: number }) => void;
  remove: () => void;
}

export default function PksLocationMap({ points, selectedId, onSelectPoint }: PksLocationMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MinimalMapHandle | null>(null);
  const onSelectRef = useRef(onSelectPoint);

  useEffect(() => {
    onSelectRef.current = onSelectPoint;
  }, [onSelectPoint]);

  const [mapFailed, setMapFailed] = useState(false);

  useEffect(() => {
    const container = containerRef.current;
    if (!container || points.length === 0) {
      return;
    }

    let cancelled = false;
    let createdMap: MinimalMapHandle | null = null;

    async function initMap() {
      try {
        const maplibregl = await import('maplibre-gl');
        if (cancelled || !container) {
          return;
        }
        const initialCenter: [number, number] = [points[0].longitude, points[0].latitude];

        const map = new maplibregl.Map({
          container,
          style: {
            version: 8,
            sources: {
              osm: {
                type: 'raster',
                tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
                tileSize: 256,
                attribution: 'OpenStreetMap contributors',
              },
            },
            layers: [
              {
                id: 'osm-tiles',
                type: 'raster',
                source: 'osm',
              },
            ],
          },
          center: initialCenter,
          zoom: 10,
        });

        map.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'top-right');

        for (const pt of points) {
          const el = document.createElement('button');
          el.type = 'button';
          el.ariaLabel = `Pilih lokasi ${pt.label}`;
          el.className =
            pt.kind === 'office'
              ? 'h-4 w-4 rounded-full border-2 border-white bg-[#B45309] shadow'
              : 'h-4 w-4 rounded-full border-2 border-white bg-[#14452F] shadow';
          el.onclick = () => onSelectRef.current(pt.id);

          new maplibregl.Marker({ element: el })
            .setLngLat([pt.longitude, pt.latitude])
            .addTo(map);
        }

        map.on('error', () => {
          // Keep marker list functional even if offline tile requests fail.
        });

        createdMap = map;
        mapRef.current = map;
      } catch {
        if (!cancelled) {
          setMapFailed(true);
        }
      }
    }

    void initMap();

    return () => {
      cancelled = true;
      mapRef.current = null;
      createdMap?.remove();
    };
  }, [points]);

  useEffect(() => {
    if (!selectedId || !mapRef.current) {
      return;
    }
    const target = points.find((p) => p.id === selectedId);
    if (target) {
      mapRef.current.flyTo({ center: [target.longitude, target.latitude], zoom: 12 });
    }
  }, [points, selectedId]);

  if (points.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-border-control bg-surface-default p-6 text-center text-sm text-ink-secondary">
        Belum ada lokasi dengan koordinat terverifikasi untuk dipetakan.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-border-subtle bg-surface-default">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border-subtle bg-surface-subtle/60 px-4 py-2.5 text-xs">
        <span className="font-semibold text-ink-primary">
          Peta Interaktif Lokasi Terverifikasi ({points.length} titik)
        </span>
        <div className="flex items-center gap-3 text-ink-secondary">
          <span className="inline-flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-full bg-accent-default" />
            Kantor Perumda
          </span>
          <span className="inline-flex items-center gap-1.5">
            <span className="inline-block h-2.5 w-2.5 rounded-full bg-primary-default" />
            PKS Mitra
          </span>
        </div>
      </div>

      {mapFailed ? (
        <div className="bg-surface-subtle p-6 text-sm text-ink-secondary">
          Tampilan kanvas peta WebGL tidak tersedia pada peramban ini. Gunakan daftar koordinat
          terverifikasi di samping untuk membuka tautan navigasi peta langsung.
        </div>
      ) : (
        <div
          ref={containerRef}
          aria-label="Peta lokasi Kantor Perumda dan PKS Mitra"
          className="h-72 w-full bg-surface-subtle sm:h-96"
        />
      )}
    </div>
  );
}
