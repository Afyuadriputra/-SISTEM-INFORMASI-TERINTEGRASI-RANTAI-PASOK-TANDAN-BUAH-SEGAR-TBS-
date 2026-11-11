import { Menu, X } from 'lucide-react';
import type { ReactNode } from 'react';
import { cn } from '@/components/atoms';
import { InternalSidebar } from '@/components/organisms';
import type { AuthenticatedUser } from '@/lib/auth/permissions';
import { isMockApiMode } from '@/lib/config/env';
import { useUiStore } from '@/lib/state/uiStore';

export interface InternalAppShellProps {
  readonly user: AuthenticatedUser;
  readonly children: ReactNode;
}

export function InternalAppShell({ user, children }: InternalAppShellProps) {
  const mobileOpen = useUiStore((s) => s.mobileDrawerOpen);
  const setMobileOpen = useUiStore((s) => s.setMobileDrawerOpen);
  const toasts = useUiStore((s) => s.toasts);
  const dismissToast = useUiStore((s) => s.dismissToast);
  const mockMode = isMockApiMode();

  return (
    <div className="min-h-screen bg-canvas">
      <InternalSidebar
        user={user}
        mobileOpen={mobileOpen}
        onCloseMobile={() => setMobileOpen(false)}
      />

      <div className="lg:pl-64">
        <header className="sticky top-0 z-20 flex items-center justify-between gap-3 border-b border-border-subtle bg-surface-default px-4 py-2.5 sm:px-6">
          <div className="flex items-center gap-3">
            <button
              id="mobile-portal-menu-trigger"
              type="button"
              onClick={() => setMobileOpen(true)}
              aria-expanded={mobileOpen}
              aria-label="Buka menu portal"
              className="inline-flex h-11 w-11 items-center justify-center rounded-md border border-border-control bg-surface-default text-ink-primary lg:hidden"
            >
              <Menu aria-hidden="true" className="h-5 w-5" />
            </button>
            <div className="min-w-0">
              <p className="truncate text-xs font-semibold uppercase tracking-wide text-ink-secondary">
                Unit Agro Niaga TBS
              </p>
              <p className="truncate text-sm font-bold text-ink-primary lg:hidden">
                {user.display_name}
              </p>
            </div>
          </div>

          <span
            className={cn(
              'rounded-sm border px-2.5 py-1 font-mono text-xs font-semibold',
              mockMode
                ? 'border-warning-text/30 bg-warning-bg text-warning-text'
                : 'border-success-text/30 bg-success-bg text-success-text',
            )}
          >
            {mockMode ? 'MODE SIMULASI (MSW)' : 'LIVE FASTAPI'}
          </span>
        </header>

        {toasts.length > 0 ? (
          <div
            aria-live="polite"
            className="mx-auto max-w-7xl space-y-2 px-4 pt-4 sm:px-6"
          >
            {toasts.map((toast) => (
              <div
                key={toast.id}
                role={toast.tone === 'danger' ? 'alert' : 'status'}
                className={cn(
                  'flex items-start justify-between gap-4 rounded-md border px-4 py-3 text-sm',
                  toast.tone === 'success' && 'border-success-text/30 bg-success-bg text-success-text',
                  toast.tone === 'warning' && 'border-warning-text/30 bg-warning-bg text-warning-text',
                  toast.tone === 'danger' && 'border-danger-text/30 bg-danger-bg text-danger-text',
                  toast.tone === 'info' && 'border-info-text/30 bg-info-bg text-info-text',
                )}
              >
                <div className="space-y-0.5">
                  <p className="font-semibold">{toast.title}</p>
                  {toast.description ? <p className="text-xs">{toast.description}</p> : null}
                  {toast.requestId ? (
                    <p className="font-mono text-[11px] opacity-90">Ref: {toast.requestId}</p>
                  ) : null}
                </div>
                <button
                  type="button"
                  aria-label="Tutup notifikasi"
                  onClick={() => dismissToast(toast.id)}
                  className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded hover:bg-black/5"
                >
                  <X aria-hidden="true" className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        ) : null}

        <main id="main-content" className="mx-auto max-w-7xl px-4 py-6 sm:px-6">
          {children}
        </main>
      </div>
    </div>
  );
}
