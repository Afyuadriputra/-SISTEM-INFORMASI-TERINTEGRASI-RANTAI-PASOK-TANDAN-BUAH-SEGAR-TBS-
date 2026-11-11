export type ApiMode = 'mock' | 'real';

export interface FrontendConfig {
  readonly apiMode: ApiMode;
  readonly apiBaseUrl: string;
  readonly appName: string;
}

function normalizeApiMode(rawValue: string | undefined): ApiMode {
  if (rawValue === 'real') {
    return 'real';
  }
  if (rawValue === 'mock' || rawValue === undefined || rawValue === '') {
    return 'mock';
  }
  throw new Error(
    `VITE_API_MODE tidak valid ("${rawValue}"). Nilai yang diizinkan: "mock" atau "real".`,
  );
}

export function getFrontendConfig(envOverride?: Partial<Record<string, string>>): FrontendConfig {
  const envSource = envOverride ?? (import.meta.env as Record<string, string | undefined>);
  const apiMode = normalizeApiMode(envSource.VITE_API_MODE);
  const rawBaseUrl = envSource.VITE_API_BASE_URL ?? '';
  const apiBaseUrl = rawBaseUrl.endsWith('/') ? rawBaseUrl.slice(0, -1) : rawBaseUrl;
  const appName = envSource.VITE_APP_NAME ?? 'AgroNiaga TBS - Perumda Tuah Sekata';

  return {
    apiMode,
    apiBaseUrl,
    appName,
  };
}

export const frontendConfig: FrontendConfig = getFrontendConfig();

export function isMockApiMode(): boolean {
  return frontendConfig.apiMode === 'mock';
}

export function assertStrictRealModeNoMockFallback(): void {
  if (frontendConfig.apiMode === 'real') {
    throw new Error('Mode REAL API aktif: fallback ke mock API dilarang.');
  }
}
