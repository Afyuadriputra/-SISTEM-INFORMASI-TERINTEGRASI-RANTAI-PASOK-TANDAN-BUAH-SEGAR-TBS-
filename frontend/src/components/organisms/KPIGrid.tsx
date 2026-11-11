import { Badge, cn } from '@/components/atoms';

export interface KPIItem {
  readonly id: string;
  readonly label: string;
  readonly value: string;
  readonly hint?: string;
  readonly simulationTag?: boolean;
  readonly tone?: 'default' | 'primary' | 'warning' | 'danger';
}

export interface KPIGridProps {
  readonly items: readonly KPIItem[];
  readonly columns?: 2 | 3 | 4;
}

const VALUE_COLOR: Record<NonNullable<KPIItem['tone']>, string> = {
  default: 'text-ink-primary',
  primary: 'text-primary-default',
  warning: 'text-warning-text',
  danger: 'text-danger-text',
};

export function KPIGrid({ items, columns = 4 }: KPIGridProps) {
  const gridCols =
    columns === 2
      ? 'grid-cols-1 sm:grid-cols-2'
      : columns === 3
        ? 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3'
        : 'grid-cols-1 sm:grid-cols-2 xl:grid-cols-4';

  return (
    <section aria-label="Ringkasan Indikator Utama" className={cn('grid gap-4', gridCols)}>
      {items.map((item) => (
        <article
          key={item.id}
          className="rounded-lg border border-border-subtle bg-surface-default p-4"
        >
          <div className="flex items-start justify-between gap-2">
            <p className="text-xs font-semibold uppercase tracking-wide text-ink-secondary">
              {item.label}
            </p>
            {item.simulationTag ? <Badge tone="warning">Simulasi</Badge> : null}
          </div>
          <p
            className={cn(
              'mt-2 font-mono text-2xl font-bold tabular-nums',
              VALUE_COLOR[item.tone ?? 'default'],
            )}
          >
            {item.value}
          </p>
          {item.hint ? <p className="mt-1.5 text-xs text-text-muted">{item.hint}</p> : null}
        </article>
      ))}
    </section>
  );
}
