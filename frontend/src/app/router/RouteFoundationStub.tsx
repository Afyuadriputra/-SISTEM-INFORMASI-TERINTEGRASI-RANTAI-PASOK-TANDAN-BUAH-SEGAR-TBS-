import { Link } from '@tanstack/react-router';
import { CANONICAL_ROUTES, ROLE_LABELS, type RoleCode } from '@/lib/auth/permissions';

interface RouteFoundationStubProps {
  readonly routePath: string;
}

export function RouteFoundationStub({ routePath }: RouteFoundationStubProps) {
  const meta = CANONICAL_ROUTES.find((entry) => entry.path === routePath);
  const roles = meta?.allowedRoles.map((r: RoleCode) => ROLE_LABELS[r]).join(', ') || 'Publik';

  return (
    <main id="main-content" className="mx-auto max-w-4xl px-4 py-10">
      <div className="rounded-lg border border-border-subtle bg-surface-default p-6 shadow-xs">
        <p className="font-mono text-xs font-semibold uppercase tracking-wide text-primary-default">
          Fondasi Rute {routePath}
        </p>
        <h1 className="mt-2 text-2xl font-bold text-ink-primary">{meta?.label ?? routePath}</h1>
        <p className="mt-2 text-sm text-ink-secondary">Akses Peran: {roles}</p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            to="/"
            className="inline-flex min-h-[44px] items-center rounded-md border border-border-control bg-surface-default px-4 text-sm font-semibold text-ink-primary hover:bg-surface-subtle"
          >
            Kembali ke Beranda
          </Link>
        </div>
      </div>
    </main>
  );
}
