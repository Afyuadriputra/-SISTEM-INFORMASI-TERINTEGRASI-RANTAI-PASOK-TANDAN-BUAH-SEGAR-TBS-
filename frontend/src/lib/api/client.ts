import type { components, paths } from '@/lib/api/generated';
import { frontendConfig } from '@/lib/config/env';
import { ApiError, parseApiErrorResponse } from '@/lib/errors/errorCatalog';
import { useUiStore } from '@/lib/state/uiStore';

export type HttpMethod = 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';

export type SuccessEnvelope<TData, TMeta = components['schemas']['SimpleSuccessMeta']> = {
  readonly success: true;
  readonly data: TData;
  readonly meta: TMeta;
  readonly request_id: string;
};

export interface RequestOptions {
  readonly path: string;
  readonly method?: HttpMethod;
  readonly query?: Record<string, string | number | boolean | null | undefined>;
  readonly body?: unknown;
  readonly headers?: Record<string, string>;
  readonly idempotencyKey?: string;
  readonly idempotencyScope?: string;
  readonly skipCsrf?: boolean;
  readonly suppressUnauthorizedHook?: boolean;
  readonly signal?: AbortSignal;
}

let cachedCsrfToken: string | null = null;
let csrfInFlight: Promise<string> | null = null;
let unauthorizedHandler: (() => void) | null = null;

export function setUnauthorizedHandler(handler: (() => void) | null): void {
  unauthorizedHandler = handler;
}

export function clearCsrfToken(): void {
  cachedCsrfToken = null;
  csrfInFlight = null;
}

export function getCachedCsrfToken(): string | null {
  return cachedCsrfToken;
}

export function buildApiUrl(
  path: string,
  query?: Record<string, string | number | boolean | null | undefined>,
): string {
  const base = frontendConfig.apiBaseUrl;
  const fullPath = `${base}${path}`;
  if (!query) {
    return fullPath;
  }
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined && value !== null && value !== '') {
      params.set(key, String(value));
    }
  }
  const qs = params.toString();
  return qs ? `${fullPath}?${qs}` : fullPath;
}

export async function ensureCsrfToken(forceRefresh = false): Promise<string> {
  if (!forceRefresh && cachedCsrfToken) {
    return cachedCsrfToken;
  }
  if (!forceRefresh && csrfInFlight) {
    return csrfInFlight;
  }

  csrfInFlight = (async () => {
    const response = await fetch(buildApiUrl('/api/v1/auth/csrf'), {
      method: 'GET',
      credentials: 'include',
      headers: {
        Accept: 'application/json',
      },
    });
    if (!response.ok) {
      throw await parseApiErrorResponse(response);
    }
    const payload = (await response.json()) as components['schemas']['CsrfEnvelope'];
    cachedCsrfToken = payload.data.csrf_token;
    return cachedCsrfToken;
  })();

  try {
    return await csrfInFlight;
  } finally {
    csrfInFlight = null;
  }
}

function isMutatingMethod(method: HttpMethod): boolean {
  return method === 'POST' || method === 'PATCH' || method === 'PUT' || method === 'DELETE';
}

export async function apiRequest<TResponse>(options: RequestOptions): Promise<TResponse> {
  const method = options.method ?? 'GET';
  const uiStore = useUiStore.getState();

  const resolvedIdempotencyKey =
    options.idempotencyKey ??
    (options.idempotencyScope
      ? uiStore.getOrCreateActionIdempotencyKey(options.idempotencyScope)
      : undefined);

  const executeAttempt = async (forceRefreshCsrf: boolean): Promise<Response> => {
    const headers: Record<string, string> = {
      Accept: 'application/json',
      ...options.headers,
    };

    const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData;
    if (options.body !== undefined && !isFormData && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    if (isMutatingMethod(method) && !options.skipCsrf) {
      const csrfToken = await ensureCsrfToken(forceRefreshCsrf);
      headers['X-CSRF-Token'] = csrfToken;
    }

    if (resolvedIdempotencyKey) {
      headers['Idempotency-Key'] = resolvedIdempotencyKey;
    }

    return fetch(buildApiUrl(options.path, options.query), {
      method,
      credentials: 'include',
      headers,
      body:
        options.body === undefined
          ? undefined
          : isFormData
            ? (options.body as FormData)
            : JSON.stringify(options.body),
      signal: options.signal,
    });
  };

  let response: Response;
  try {
    response = await executeAttempt(false);
  } catch (err) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError({
      status: 503,
      code: 'SYS_DEPENDENCY_UNAVAILABLE',
      message: 'Tidak dapat terhubung ke server API. Periksa koneksi atau status layanan backend.',
    });
  }

  if (response.status === 403 && isMutatingMethod(method) && !options.skipCsrf) {
    const firstError = await parseApiErrorResponse(response.clone());
    if (firstError.code === 'AUTH_CSRF_INVALID') {
      clearCsrfToken();
      response = await executeAttempt(true);
    }
  }

  if (!response.ok) {
    const apiError = await parseApiErrorResponse(response);
    if (response.status === 401) {
      clearCsrfToken();
      if (!options.suppressUnauthorizedHook) {
        unauthorizedHandler?.();
      }
    }
    if (options.idempotencyScope && !apiError.retryable && response.status < 500) {
      uiStore.clearActionIdempotencyKey(options.idempotencyScope);
    }
    throw apiError;
  }

  if (options.idempotencyScope) {
    uiStore.clearActionIdempotencyKey(options.idempotencyScope);
  }

  return (await response.json()) as TResponse;
}

export async function apiDownloadBlob(path: string): Promise<{ blob: Blob; filename: string }> {
  const response = await fetch(buildApiUrl(path), {
    method: 'GET',
    credentials: 'include',
  });
  if (!response.ok) {
    const apiError = await parseApiErrorResponse(response);
    if (response.status === 401) {
      clearCsrfToken();
      unauthorizedHandler?.();
    }
    throw apiError;
  }
  const disposition = response.headers.get('Content-Disposition') ?? '';
  const match = /filename="?([^";]+)"?/i.exec(disposition);
  const filename = match?.[1] ?? 'dokumen-bukti';
  const blob = await response.blob();
  return { blob, filename };
}

export type OpenApiPaths = paths;
