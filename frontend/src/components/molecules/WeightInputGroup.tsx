import { Input } from '@/components/atoms';
import { computeNettoPreview, formatKg } from '@/lib/decimal/precision';
import { FormField } from './FormField';

export interface WeightInputGroupProps {
  readonly grossValue: string;
  readonly tareValue: string;
  readonly onGrossChange: (val: string) => void;
  readonly onTareChange: (val: string) => void;
  readonly grossError?: string;
  readonly tareError?: string;
  readonly disabled?: boolean;
}

export function WeightInputGroup({
  grossValue,
  tareValue,
  onGrossChange,
  onTareChange,
  grossError,
  tareError,
  disabled = false,
}: WeightInputGroupProps) {
  const preview = computeNettoPreview(grossValue, tareValue);

  return (
    <div className="space-y-3 rounded-lg border border-border-subtle bg-surface-subtle/50 p-4">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <FormField
          id="weight-gross-input"
          label="Berat Bruto (kg)"
          required
          helperText="Gunakan maksimal 3 desimal (contoh: 4250.500)"
          error={grossError}
        >
          <Input
            id="weight-gross-input"
            type="text"
            inputMode="decimal"
            monospace
            disabled={disabled}
            hasError={Boolean(grossError)}
            placeholder="0.000"
            value={grossValue}
            onChange={(e) => onGrossChange(e.target.value)}
          />
        </FormField>
        <FormField
          id="weight-tare-input"
          label="Berat Tara (kg)"
          required
          helperText="Berat wadah atau kendaraan kosong"
          error={tareError}
        >
          <Input
            id="weight-tare-input"
            type="text"
            inputMode="decimal"
            monospace
            disabled={disabled}
            hasError={Boolean(tareError)}
            placeholder="0.000"
            value={tareValue}
            onChange={(e) => onTareChange(e.target.value)}
          />
        </FormField>
      </div>
      <div className="flex flex-col gap-1 rounded-md border border-border-subtle bg-surface-default px-3.5 py-2.5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-ink-secondary">
            Pratinjau Berat Netto
          </p>
          <p className="text-xs text-text-muted">
            Pratinjau antarmuka. Nilai resmi tetap dihitung server (BR-TBS-004).
          </p>
        </div>
        {preview.valid && preview.nettoString !== null ? (
          <p className="font-mono text-lg font-bold text-primary-default tabular-nums">
            {formatKg(preview.nettoString)}
          </p>
        ) : (
          <p className="text-xs font-medium text-warning-text">
            {grossValue || tareValue ? preview.errorMessage : 'Menunggu input Bruto dan Tara'}
          </p>
        )}
      </div>
    </div>
  );
}
