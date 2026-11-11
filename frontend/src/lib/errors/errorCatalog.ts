import { ERROR_CATALOG, type ErrorCatalogEntry, type ErrorCode } from './errorCatalogData';

export { ERROR_CATALOG };
export type { ErrorCatalogEntry, ErrorCode };

export interface FieldValidationDetail {
  readonly field?: string;
  readonly loc?: ReadonlyArray<string | number>;
  readonly message?: string;
  readonly msg?: string;
}

export interface ApiErrorPayload {
  readonly success: false;
  readonly error: {
    readonly code: string;
    readonly message: string;
    readonly details: unknown;
  };
  readonly request_id?: string;
}

export class ApiError extends Error {
  readonly status: number;
  readonly code: ErrorCode | string;
  readonly details: unknown;
  readonly requestId: string | null;
  readonly retryable: boolean;
  readonly actionHint: string;

  constructor(params: {
    status: number;
    code: string;
    message?: string;
    details?: unknown;
    requestId?: string | null;
  }) {
    const entry = getErrorMetadata(params.code);
    const resolvedMessage =
      params.message && params.message.trim().length > 0
        ? params.message
        : (entry?.message ?? 'Terjadi kendala pada sistem.');
    super(resolvedMessage);
    this.name = 'ApiError';
    this.status = params.status || entry?.httpStatus || 500;
    this.code = params.code;
    this.details = params.details ?? null;
    this.requestId = params.requestId ?? null;
    this.retryable = entry?.retryable ?? this.status >= 500;
    this.actionHint =
      entry?.action ?? 'Periksa kembali data Anda atau coba beberapa saat lagi.';
  }
}

export function isKnownErrorCode(code: string): code is ErrorCode {
  return Object.prototype.hasOwnProperty.call(ERROR_CATALOG, code);
}

export function getErrorMetadata(code: string): ErrorCatalogEntry | null {
  if (isKnownErrorCode(code)) {
    return ERROR_CATALOG[code];
  }
  return null;
}

export function getSafeErrorMessage(code: string, fallback?: string): string {
  const entry = getErrorMetadata(code);
  if (entry) {
    return entry.message;
  }
  return fallback && fallback.trim().length > 0 ? fallback : 'Terjadi kendala pada permintaan.';
}

export function extractFieldErrors(details: unknown): Record<string, string> {
  const map: Record<string, string> = {};
  if (!details) {
    return map;
  }

  if (Array.isArray(details)) {
    for (const item of details) {
      if (typeof item === 'object' && item !== null) {
        const entry = item as FieldValidationDetail;
        const fieldName =
          entry.field ??
          (Array.isArray(entry.loc) ? String(entry.loc[entry.loc.length - 1] ?? '') : '');
        const msg = entry.message ?? entry.msg ?? '';
        if (fieldName && msg) {
          map[fieldName] = msg;
        }
      }
    }
    return map;
  }

  if (typeof details === 'object') {
    const obj = details as Record<string, unknown>;
    if (Array.isArray(obj.fields)) {
      return extractFieldErrors(obj.fields);
    }
    for (const [key, value] of Object.entries(obj)) {
      if (typeof value === 'string' && value.trim().length > 0) {
        map[key] = value;
      } else if (Array.isArray(value) && typeof value[0] === 'string') {
        map[key] = value[0];
      }
    }
  }

  return map;
}

export async function parseApiErrorResponse(response: Response): Promise<ApiError> {
  const headerRequestId = response.headers.get('X-Request-Id');
  try {
    const body = (await response.json()) as Partial<ApiErrorPayload>;
    if (body && typeof body === 'object' && body.error && typeof body.error.code === 'string') {
      return new ApiError({
        status: response.status,
        code: body.error.code,
        message: body.error.message,
        details: body.error.details ?? null,
        requestId: body.request_id ?? headerRequestId,
      });
    }
  } catch {
    // Non-JSON upstream error responses map to HTTP fallback code cleanly.
  }

  const fallbackCode: ErrorCode =
    response.status === 401
      ? 'AUTH_REQUIRED'
      : response.status === 403
        ? 'AUTH_ACCESS_DENIED'
        : response.status === 404
          ? 'SYS_RESOURCE_NOT_FOUND'
          : response.status === 429
            ? 'SYS_RATE_LIMIT_EXCEEDED'
            : response.status === 503
              ? 'SYS_DEPENDENCY_UNAVAILABLE'
              : response.status === 504
                ? 'SYS_REQUEST_TIMEOUT'
                : 'SYS_INTERNAL_ERROR';

  return new ApiError({
    status: response.status,
    code: fallbackCode,
    requestId: headerRequestId,
  });
}
