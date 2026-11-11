import { Link, Outlet } from '@tanstack/react-router';
import { Suspense } from 'react';
import { getRoleHomePath, type AuthenticatedUser } from '@/lib/auth/permissions';
import { useUiStore } from '@/lib/state/uiStore';

export function LoadingFallback() {
  return (
    <div
      role="status"
      aria-live="polite"
      className="flex min-h-[50vh] items-center justify-center px-4 text-sm text-ink-secondary"
    >
      Memuat halaman...
    </div>
  );
}

export function NotFoundView() {
  return (
    <main id="main-content" className="mx-auto max-w-xl px-4 py-16">
      <div className="rounded-lg border border-border-subtle bg-surface-default p-6">
        <p className="font-mono text-xs font-semibold uppercase text-accent-default">HTTP 404</p>
        <h1 className="mt-2 text-2xl font-bold text-ink-primary">Halaman Tidak Ditemukan</h1>
        <p className="mt-2 text-sm text-ink-secondary">
          Alamat yang Anda buka tidak tersedia di sistem AgroNiaga TBS.
        </p>
        <div className="mt-6">
          <Link
            to="/"
            className="inline-flex min-h-[44px] items-center rounded-md bg-primary-default px-4 text-sm font-semibold text-primary-foreground hover:bg-brand-hover"
          >
            Kembali ke Beranda
          </Link>
        </div>
      </div>
    </main>
  );
}

export function ForbiddenRoleView({ user }: { readonly user: AuthenticatedUser | null }) {
  const homePath = getRoleHomePath(user);
  return (
    <main id="main-content" className="mx-auto max-w-xl px-4 py-16">
      <div className="rounded-lg border border-border-subtle bg-surface-default p-6">
        <p className="font-mono text-xs font-semibold uppercase text-danger-text">
          AUTH_ACCESS_DENIED (403)
        </p>
        <h1 className="mt-2 text-2xl font-bold text-ink-primary">Akses Dibatasi Berdasarkan Peran</h1>
        <p className="mt-2 text-sm text-ink-secondary">
          Akun Anda tidak memiliki kewenangan untuk membuka halaman ini.
        </p>
        <div className="mt-6">
          <Link
            to={homePath}
            className="inline-flex min-h-[44px] items-center rounded-md bg-primary-default px-4 text-sm font-semibold text-primary-foreground hover:bg-brand-hover"
          >
            Kembali ke Beranda Peran
          </Link>
        </div>
      </div>
    </main>
  );
}

export function RootLayout() {
  const sessionExpired = useUiStore((s) => s.sessionExpiredBanner);
  const dismissSessionBanner = useUiStore((s) => s.setSessionExpiredBanner);
  return (
    <div className="min-h-screen bg-canvas text-ink-primary">
      <a href="#main-content" className="skip-link">
        Lewati ke konten utama
      </a>
      {sessionExpired ? (
        <div
          role="alert"
          className="border-b border-warning-text/20 bg-warning-bg px-4 py-2 text-sm text-warning-text"
        >
          <div className="mx-auto flex max-w-7xl items-center justify-between gap-4">
            <span>Sesi Anda berakhir. Silakan masuk kembali untuk melanjutkan.</span>
            <button
              type="button"
              onClick={() => dismissSessionBanner(false)}
              className="font-semibold underline"
            >
              Tutup
            </button>
          </div>
        </div>
      ) : null}
      <Suspense fallback={<LoadingFallback />}>
        <Outlet />
      </Suspense>
    </div>
  );
}
