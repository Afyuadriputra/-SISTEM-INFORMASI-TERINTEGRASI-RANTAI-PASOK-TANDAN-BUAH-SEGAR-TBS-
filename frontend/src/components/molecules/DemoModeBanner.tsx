import { isDemoBannerEnabled } from '@/lib/config/env';

export interface DemoModeBannerProps {
  readonly variant?: 'bar' | 'badge';
}

/** Explicit non-operational marker rendered only when VITE_DEMO_BANNER=true. */
export function DemoModeBanner({ variant = 'bar' }: DemoModeBannerProps) {
  if (!isDemoBannerEnabled()) {
    return null;
  }

  if (variant === 'badge') {
    return (
      <span className="rounded-sm border border-warning-text/40 bg-warning-bg px-2 py-1 font-mono text-[11px] font-semibold whitespace-nowrap text-warning-text">
        MODE DEMO — DATA SINTETIS
      </span>
    );
  }

  return (
    <div
      role="note"
      className="border-b border-warning-text/30 bg-warning-bg px-4 py-1.5 text-center text-xs font-semibold text-warning-text"
    >
      MODE DEMO — DATA SINTETIS: Data simulasi lokal (database agroniaga_demo), bukan data operasional resmi Perumda.
    </div>
  );
}
