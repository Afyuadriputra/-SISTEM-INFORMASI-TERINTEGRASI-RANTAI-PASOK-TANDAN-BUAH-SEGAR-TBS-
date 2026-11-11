import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/atoms';

export interface PaginationControlProps {
  readonly page: number;
  readonly totalPages: number;
  readonly totalItems: number;
  readonly pageSize: number;
  readonly hasPrev: boolean;
  readonly hasNext: boolean;
  readonly onPageChange: (nextPage: number) => void;
}

export function PaginationControl({
  page,
  totalPages,
  totalItems,
  pageSize,
  hasPrev,
  hasNext,
  onPageChange,
}: PaginationControlProps) {
  const startItem = totalItems === 0 ? 0 : (page - 1) * pageSize + 1;
  const endItem = Math.min(totalItems, page * pageSize);

  return (
    <nav
      aria-label="Navigasi halaman tabel"
      className="flex flex-col gap-3 border-t border-border-subtle pt-4 sm:flex-row sm:items-center sm:justify-between"
    >
      <p className="text-xs text-ink-secondary tabular-nums">
        Menampilkan <span className="font-semibold text-ink-primary">{startItem}</span> sampai{' '}
        <span className="font-semibold text-ink-primary">{endItem}</span> dari{' '}
        <span className="font-semibold text-ink-primary">{totalItems}</span> data (Halaman{' '}
        {totalPages === 0 ? 0 : page} dari {totalPages})
      </p>
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          disabled={!hasPrev}
          onClick={() => onPageChange(page - 1)}
          leadingIcon={<ChevronLeft aria-hidden="true" className="h-4 w-4" />}
        >
          Sebelumnya
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={!hasNext}
          onClick={() => onPageChange(page + 1)}
          leadingIcon={<ChevronRight aria-hidden="true" className="h-4 w-4" />}
        >
          Berikutnya
        </Button>
      </div>
    </nav>
  );
}
