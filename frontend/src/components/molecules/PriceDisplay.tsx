import { Badge } from '@/components/atoms';
import { formatPricePerKg, formatWibDateTime } from '@/lib/decimal/precision';

export interface PriceDisplayProps {
  readonly pricePerKg: string;
  readonly categoryName: string;
  readonly sourceName: string;
  readonly updatedAt: string;
  readonly isExpired?: boolean;
  readonly isSimulation?: boolean;
  readonly emphasis?: 'default' | 'hero';
}

export function PriceDisplay({
  pricePerKg,
  categoryName,
  sourceName,
  updatedAt,
  isExpired = false,
  isSimulation = false,
  emphasis = 'default',
}: PriceDisplayProps) {
  return (
    <div className="space-y-1">
      <div className="flex flex-wrap items-center gap-2">
        <span
          className={
            emphasis === 'hero'
              ? 'font-mono text-2xl font-bold text-primary-default tabular-nums'
              : 'font-mono text-lg font-bold text-ink-primary tabular-nums'
          }
        >
          {formatPricePerKg(pricePerKg)}
        </span>
        {isExpired ? <Badge tone="warning">Kedaluwarsa</Badge> : null}
        {isSimulation ? <Badge tone="warning">Data Simulasi</Badge> : null}
      </div>
      <p className="text-xs font-medium text-ink-secondary">{categoryName}</p>
      <p className="text-xs text-text-muted">
        Sumber: {sourceName} | Pembaruan: {formatWibDateTime(updatedAt)}
      </p>
    </div>
  );
}
