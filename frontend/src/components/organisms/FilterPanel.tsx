import type { ReactNode } from 'react';
import { cn } from '@/components/atoms';

export interface FilterPanelProps {
  readonly children: ReactNode;
  readonly onReset?: () => void;
  readonly className?: string;
}

export function FilterPanel({ children, onReset, className }: FilterPanelProps) {
  return (
    <section
      aria-label="Filter Data"
      className={cn(
        'rounded-lg border border-border-subtle bg-surface-default p-4',
        className,
      )}
    >
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
        <div className="grid flex-1 grid-cols-1 gap-3 sm:grid-cols-2 lg:flex lg:flex-wrap lg:items-end">
          {children}
        </div>
        {onReset ? (
          <button
            type="button"
            onClick={onReset}
            className="inline-flex min-h-[44px] shrink-0 items-center justify-center rounded-md border border-border-control bg-surface-default px-3 text-xs font-semibold text-ink-secondary hover:bg-surface-subtle hover:text-ink-primary"
          >
            Atur Ulang Filter
          </button>
        ) : null}
      </div>
    </section>
  );
}
