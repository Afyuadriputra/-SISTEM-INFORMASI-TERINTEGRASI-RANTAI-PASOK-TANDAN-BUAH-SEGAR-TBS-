import { Input } from '@/components/atoms';

export interface DateRangeFilterProps {
  readonly fromDate: string;
  readonly toDate: string;
  readonly onFromChange: (value: string) => void;
  readonly onToChange: (value: string) => void;
  readonly fromLabel?: string;
  readonly toLabel?: string;
}

export function DateRangeFilter({
  fromDate,
  toDate,
  onFromChange,
  onToChange,
  fromLabel = 'Tanggal Mulai',
  toLabel = 'Tanggal Akhir',
}: DateRangeFilterProps) {
  const isInvalidRange = Boolean(fromDate && toDate && fromDate > toDate);
  return (
    <div className="space-y-1">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
        <div className="flex-1">
          <label htmlFor="filter-date-from" className="mb-1 block text-xs font-semibold text-ink-secondary">
            {fromLabel}
          </label>
          <Input
            id="filter-date-from"
            type="date"
            value={fromDate}
            hasError={isInvalidRange}
            onChange={(e) => onFromChange(e.target.value)}
          />
        </div>
        <div className="flex-1">
          <label htmlFor="filter-date-to" className="mb-1 block text-xs font-semibold text-ink-secondary">
            {toLabel}
          </label>
          <Input
            id="filter-date-to"
            type="date"
            value={toDate}
            hasError={isInvalidRange}
            onChange={(e) => onToChange(e.target.value)}
          />
        </div>
      </div>
      {isInvalidRange ? (
        <p role="alert" className="text-xs font-medium text-danger-text">
          Tanggal akhir tidak boleh mendahului tanggal mulai.
        </p>
      ) : null}
    </div>
  );
}
