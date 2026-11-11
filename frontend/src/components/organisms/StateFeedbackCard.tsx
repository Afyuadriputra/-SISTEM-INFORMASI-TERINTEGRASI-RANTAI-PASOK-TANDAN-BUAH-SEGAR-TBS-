import { AlertCircle, Inbox, RefreshCw } from 'lucide-react';
import { Button, SkeletonRow } from '@/components/atoms';
import { ApiError } from '@/lib/errors/errorCatalog';

export interface StateFeedbackCardProps {
  readonly variant: 'loading' | 'empty' | 'error';
  readonly title?: string;
  readonly description?: string;
  readonly error?: unknown;
  readonly actionLabel?: string;
  readonly onAction?: () => void;
}

export function StateFeedbackCard({
  variant,
  title,
  description,
  error,
  actionLabel,
  onAction,
}: StateFeedbackCardProps) {
  if (variant === 'loading') {
    return (
      <div
        role="status"
        aria-live="polite"
        className="rounded-lg border border-border-subtle bg-surface-default p-6"
      >
        <p className="mb-3 text-sm font-semibold text-ink-secondary">
          {title ?? 'Sedang memuat data...'}
        </p>
        <SkeletonRow lines={4} />
      </div>
    );
  }

  if (variant === 'empty') {
    return (
      <div className="rounded-lg border border-dashed border-border-control bg-surface-default p-8 text-center">
        <Inbox aria-hidden="true" className="mx-auto h-7 w-7 text-text-muted" />
        <p className="mt-3 text-base font-bold text-ink-primary">{title ?? 'Data Belum Tersedia'}</p>
        <p className="mx-auto mt-1 max-w-md text-sm text-ink-secondary">
          {description ?? 'Belum ada catatan yang cocok dengan filter aktif saat ini.'}
        </p>
        {onAction ? (
          <div className="mt-5">
            <Button variant="outline" onClick={onAction}>
              {actionLabel ?? 'Muat Ulang Data'}
            </Button>
          </div>
        ) : null}
      </div>
    );
  }

  const apiErr = error instanceof ApiError ? error : null;
  const resolvedTitle = title ?? (apiErr ? `Gagal Memuat (${apiErr.code})` : 'Gagal Memuat Data');
  const resolvedDescription =
    description ??
    (apiErr
      ? `${apiErr.message} ${apiErr.actionHint}`
      : 'Terjadi kendala saat mengambil data dari server.');

  return (
    <div
      role="alert"
      className="rounded-lg border border-danger-text/30 bg-danger-bg/60 p-6 text-danger-text"
    >
      <div className="flex items-start gap-3">
        <AlertCircle aria-hidden="true" className="mt-0.5 h-5 w-5 shrink-0 text-danger-solid" />
        <div className="space-y-2">
          <h2 className="text-base font-bold">{resolvedTitle}</h2>
          <p className="text-sm text-ink-primary">{resolvedDescription}</p>
          {apiErr?.requestId ? (
            <p className="font-mono text-xs text-ink-secondary">
              Kode Referensi (Request ID): {apiErr.requestId}
            </p>
          ) : null}
          {onAction ? (
            <div className="pt-2">
              <Button
                variant="outline"
                size="sm"
                onClick={onAction}
                leadingIcon={<RefreshCw aria-hidden="true" className="h-4 w-4" />}
              >
                {actionLabel ?? 'Coba Lagi'}
              </Button>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
