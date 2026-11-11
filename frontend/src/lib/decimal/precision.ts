import Decimal from 'decimal.js';

Decimal.set({
  precision: 28,
  rounding: Decimal.ROUND_HALF_UP,
});

export type DecimalLike = string | Decimal;

const DECIMAL_NUMBER_REGEX = /^-?\d+(?:\.\d+)?$/;

export function parseDecimalStrict(raw: string): Decimal | null {
  const trimmed = raw.trim();
  if (!trimmed) {
    return null;
  }

  // Normalize unambiguous comma decimal input ("2450,500" -> "2450.500") when no dot is present.
  let normalized = trimmed;
  if (trimmed.includes(',') && !trimmed.includes('.')) {
    const commaParts = trimmed.split(',');
    if (commaParts.length === 2) {
      normalized = `${commaParts[0]}.${commaParts[1]}`;
    } else {
      return null;
    }
  }

  if (!DECIMAL_NUMBER_REGEX.test(normalized)) {
    return null;
  }

  try {
    const d = new Decimal(normalized);
    return d.isFinite() ? d : null;
  } catch {
    return null;
  }
}

export function toFixedDecimalString(value: DecimalLike | null | undefined, scale: number): string | null {
  if (value === null || value === undefined) {
    return null;
  }
  const d = typeof value === 'string' ? parseDecimalStrict(value) : value;
  if (!d) {
    return null;
  }
  return d.toFixed(scale);
}

function formatLocalizedDecimal(
  value: DecimalLike | null | undefined,
  decimals: number,
): string | null {
  if (value === null || value === undefined) {
    return null;
  }
  const d = typeof value === 'string' ? parseDecimalStrict(value) : value;
  if (!d) {
    return null;
  }

  const fixed = d.toFixed(decimals);
  const isNegative = fixed.startsWith('-');
  const unsigned = isNegative ? fixed.slice(1) : fixed;
  const [intPart = '0', fracPart] = unsigned.split('.');
  const formattedInt = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  const sign = isNegative ? '-' : '';
  return decimals > 0 && fracPart !== undefined
    ? `${sign}${formattedInt},${fracPart}`
    : `${sign}${formattedInt}`;
}

export function formatKg(value: DecimalLike | null | undefined): string {
  const formatted = formatLocalizedDecimal(value, 3);
  return formatted ? `${formatted} kg` : '-';
}

export function formatTonnesFromKg(value: DecimalLike | null | undefined): string {
  if (value === null || value === undefined) {
    return '-';
  }
  const d = typeof value === 'string' ? parseDecimalStrict(value) : value;
  if (!d) {
    return '-';
  }
  const tonnes = d.div(1000);
  const formatted = formatLocalizedDecimal(tonnes, 2);
  return formatted ? `${formatted} ton` : '-';
}

export function formatPricePerKg(value: DecimalLike | null | undefined): string {
  const formatted = formatLocalizedDecimal(value, 2);
  return formatted ? `Rp ${formatted}/kg` : '-';
}

export function formatIdr(value: DecimalLike | null | undefined): string {
  const formatted = formatLocalizedDecimal(value, 2);
  if (!formatted) {
    return '-';
  }
  if (formatted.startsWith('-')) {
    return `-Rp ${formatted.slice(1)}`;
  }
  return `Rp ${formatted}`;
}

export function formatPercent(value: DecimalLike | null | undefined): string {
  const formatted = formatLocalizedDecimal(value, 4);
  return formatted ? `${formatted}%` : '-';
}

export function formatHectares(value: DecimalLike | null | undefined): string {
  const formatted = formatLocalizedDecimal(value, 4);
  return formatted ? `${formatted} ha` : '-';
}

export function formatIntegerCount(value: number | null | undefined): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return '-';
  }
  return new Intl.NumberFormat('id-ID', { maximumFractionDigits: 0 }).format(value);
}

export interface NettoPreviewResult {
  readonly valid: boolean;
  readonly nettoString: string | null;
  readonly errorMessage: string | null;
}

/**
 * Computes UI-only preview Netto weight from Bruto and Tara strings using Decimal.
 * Authoritative netto persistence stays on the backend (BR-TBS-004).
 */
export function computeNettoPreview(grossRaw: string, tareRaw: string): NettoPreviewResult {
  const gross = parseDecimalStrict(grossRaw);
  const tare = parseDecimalStrict(tareRaw);

  if (!gross || !tare) {
    return { valid: false, nettoString: null, errorMessage: 'Masukkan angka Bruto dan Tara yang valid.' };
  }
  if (gross.isNegative() || tare.isNegative()) {
    return { valid: false, nettoString: null, errorMessage: 'Nilai berat tidak boleh negatif.' };
  }
  if (tare.greaterThan(gross)) {
    return {
      valid: false,
      nettoString: null,
      errorMessage: 'Berat tara tidak boleh melebihi berat bruto.',
    };
  }

  return {
    valid: true,
    nettoString: gross.minus(tare).toFixed(3),
    errorMessage: null,
  };
}

export interface ReconciliationPreviewResult {
  readonly differenceKg: string;
  readonly differencePercent: string;
  readonly isNegativeDifference: boolean;
  readonly exceedsTolerance: boolean;
}

/**
 * Computes UI-only preview diff & percentage for reconciliation checks (BR-REC-001/002/004).
 */
export function computeReconciliationDiffPreview(
  originKgRaw: string,
  millKgRaw: string,
  tolerancePercentRaw: string,
): ReconciliationPreviewResult | null {
  const origin = parseDecimalStrict(originKgRaw);
  const mill = parseDecimalStrict(millKgRaw);
  const tol = parseDecimalStrict(tolerancePercentRaw);
  if (!origin || !mill || !tol || origin.lessThanOrEqualTo(0)) {
    return null;
  }

  const diff = origin.minus(mill);
  const pct = diff.div(origin).times(100);
  const absPct = pct.abs();
  return {
    differenceKg: diff.toFixed(3),
    differencePercent: pct.toFixed(4),
    isNegativeDifference: diff.isNegative(),
    exceedsTolerance: absPct.greaterThan(tol) || diff.isNegative(),
  };
}

const wibDateTimeFormatter = new Intl.DateTimeFormat('id-ID', {
  timeZone: 'Asia/Jakarta',
  day: '2-digit',
  month: 'short',
  year: 'numeric',
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
});

const wibDateFormatter = new Intl.DateTimeFormat('id-ID', {
  timeZone: 'Asia/Jakarta',
  day: '2-digit',
  month: 'short',
  year: 'numeric',
});

const CALENDAR_DATE_REGEX = /^(\d{4})-(\d{2})-(\d{2})$/;
const INDONESIAN_MONTHS_SHORT = [
  'Jan',
  'Feb',
  'Mar',
  'Apr',
  'Mei',
  'Jun',
  'Jul',
  'Agu',
  'Sep',
  'Okt',
  'Nov',
  'Des',
] as const;

export function formatWibDateTime(isoUtc: string | null | undefined): string {
  if (!isoUtc) {
    return '-';
  }
  const date = new Date(isoUtc);
  if (Number.isNaN(date.getTime())) {
    return '-';
  }
  return `${wibDateTimeFormatter.format(date)} WIB`;
}

/**
 * Renders pure YYYY-MM-DD calendar dates without timezone shift, or UTC timestamps in WIB.
 */
export function formatCalendarOrWibDate(rawDate: string | null | undefined): string {
  if (!rawDate) {
    return '-';
  }
  const calMatch = CALENDAR_DATE_REGEX.exec(rawDate.trim());
  if (calMatch) {
    const year = calMatch[1];
    const monthIndex = Number(calMatch[2]) - 1;
    const day = calMatch[3];
    const monthLabel = INDONESIAN_MONTHS_SHORT[monthIndex];
    if (!monthLabel) {
      return rawDate;
    }
    return `${day} ${monthLabel} ${year}`;
  }
  const parsed = new Date(rawDate);
  if (Number.isNaN(parsed.getTime())) {
    return '-';
  }
  return wibDateFormatter.format(parsed);
}
