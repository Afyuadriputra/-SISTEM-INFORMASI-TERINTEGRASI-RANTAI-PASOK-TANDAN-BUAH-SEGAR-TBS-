import type { ReactNode } from 'react';
import { SkeletonRow, cn } from '@/components/atoms';

export interface DataTableColumn<TRow> {
  readonly key: string;
  readonly header: string;
  readonly align?: 'left' | 'right';
  readonly className?: string;
  readonly render: (row: TRow) => ReactNode;
}

export interface DataTableProps<TRow> {
  readonly caption: string;
  readonly rows: readonly TRow[];
  readonly columns: readonly DataTableColumn<TRow>[];
  readonly getRowKey: (row: TRow) => string;
  readonly isLoading?: boolean;
  readonly emptyTitle?: string;
  readonly emptyDescription?: string;
}

export function DataTable<TRow>({
  caption,
  rows,
  columns,
  getRowKey,
  isLoading = false,
  emptyTitle = 'Belum ada data',
  emptyDescription = 'Ubah kata kunci pencarian atau tambah data baru.',
}: DataTableProps<TRow>) {
  if (isLoading) {
    return (
      <div
        role="status"
        aria-live="polite"
        className="rounded-lg border border-border-subtle bg-surface-default p-6"
      >
        <p className="mb-3 text-xs font-semibold text-ink-secondary">Memuat tabel data...</p>
        <SkeletonRow lines={4} />
      </div>
    );
  }

  if (rows.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-border-control bg-surface-default p-8 text-center">
        <p className="text-sm font-semibold text-ink-primary">{emptyTitle}</p>
        <p className="mt-1 text-xs text-ink-secondary">{emptyDescription}</p>
      </div>
    );
  }

  return (
    <div className="w-full overflow-x-auto rounded-lg border border-border-subtle bg-surface-default">
      <table className="min-w-full border-collapse text-left text-sm">
        <caption className="sr-only">{caption}</caption>
        <thead className="border-b border-border-subtle bg-surface-subtle/80 text-xs font-bold uppercase tracking-wide text-ink-secondary">
          <tr>
            {columns.map((col) => (
              <th
                key={col.key}
                scope="col"
                className={cn(
                  'whitespace-nowrap px-4 py-3',
                  col.align === 'right' ? 'text-right' : 'text-left',
                  col.className,
                )}
              >
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border-subtle text-ink-primary">
          {rows.map((row) => (
            <tr key={getRowKey(row)} className="hover:bg-surface-subtle/40">
              {columns.map((col) => (
                <td
                  key={col.key}
                  className={cn(
                    'px-4 py-3 align-top',
                    col.align === 'right' ? 'text-right tabular-nums' : 'text-left',
                    col.className,
                  )}
                >
                  {col.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
