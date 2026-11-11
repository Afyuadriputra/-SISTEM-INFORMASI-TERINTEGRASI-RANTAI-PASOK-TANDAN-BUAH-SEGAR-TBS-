import { Link, useNavigate, useRouterState } from '@tanstack/react-router';
import { LogOut, ShieldAlert, Sprout, X } from 'lucide-react';
import { useState } from 'react';
import { Button, cn } from '@/components/atoms';
import {
  ROLE_LABELS,
  isNonApproverAdmin,
  type AuthenticatedUser,
} from '@/lib/auth/permissions';
import { logoutSession } from '@/lib/auth/session';
import { getInternalNavItemsForRoles } from './navigationConfig';

export interface InternalSidebarProps {
  readonly user: AuthenticatedUser;
  readonly mobileOpen: boolean;
  readonly onCloseMobile: () => void;
}

export function InternalSidebar({ user, mobileOpen, onCloseMobile }: InternalSidebarProps) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const navigate = useNavigate();
  const [loggingOut, setLoggingOut] = useState(false);

  const navItems = getInternalNavItemsForRoles(user.roles);
  const primaryRoleLabel = user.roles.map((r) => ROLE_LABELS[r] ?? r).join(', ');
  const isNonApprover = isNonApproverAdmin(user);

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await logoutSession();
      onCloseMobile();
      await navigate({ to: '/login', replace: true });
    } finally {
      setLoggingOut(false);
    }
  };

  const sidebarContent = (
    <aside
      data-sidebar-surface="dark"
      aria-label="Navigasi Portal Internal"
      className="flex h-full w-64 flex-col justify-between bg-sidebar-bg text-sidebar-text"
    >
      <div>
        <div className="flex items-center justify-between border-b border-white/10 px-4 py-4">
          <Link
            to="/"
            onClick={onCloseMobile}
            className="flex min-w-0 items-center gap-2.5 text-sidebar-text no-underline"
          >
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-sidebar-active text-white">
              <Sprout aria-hidden="true" className="h-5 w-5" />
            </span>
            <span className="min-w-0">
              <span className="block truncate text-sm font-bold leading-tight">AgroNiaga TBS</span>
              <span className="block truncate text-xs text-sidebar-muted">Portal Internal</span>
            </span>
          </Link>
          <button
            type="button"
            onClick={onCloseMobile}
            aria-label="Tutup panel menu"
            className="inline-flex h-10 w-10 items-center justify-center rounded-md text-sidebar-muted hover:bg-white/10 hover:text-white lg:hidden"
          >
            <X aria-hidden="true" className="h-5 w-5" />
          </button>
        </div>

        <div className="border-b border-white/10 px-4 py-3.5">
          <p className="truncate text-sm font-semibold text-sidebar-text">{user.display_name}</p>
          <p className="mt-0.5 truncate text-xs text-sidebar-muted">{primaryRoleLabel}</p>
          {isNonApprover ? (
            <div className="mt-2 inline-flex items-center gap-1.5 rounded bg-warning-bg/15 px-2 py-1 text-[11px] font-semibold text-warning-bg">
              <ShieldAlert aria-hidden="true" className="h-3.5 w-3.5 shrink-0" />
              <span>Non-Approver (BR-SYS-002)</span>
            </div>
          ) : null}
        </div>

        <nav className="space-y-1 px-3 py-4">
          {navItems.map((item) => {
            const isExactPortalBase =
              item.to === '/app/petani' ||
              item.to === '/app/koperasi' ||
              item.to === '/app/perumda' ||
              item.to === '/app/pks' ||
              item.to === '/app/direksi' ||
              item.to === '/app/admin';
            const active = isExactPortalBase
              ? pathname === item.to
              : pathname === item.to || pathname.startsWith(`${item.to}/`);

            return (
              <Link
                key={item.to}
                to={item.to}
                onClick={onCloseMobile}
                aria-current={active ? 'page' : undefined}
                className={cn(
                  'flex min-h-[44px] items-center rounded-md px-3 text-sm font-medium transition-colors',
                  active
                    ? 'bg-sidebar-active font-semibold text-sidebar-text'
                    : 'text-sidebar-muted hover:bg-white/10 hover:text-sidebar-text',
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="border-t border-white/10 p-3">
        <Link
          to="/harga-tbs"
          onClick={onCloseMobile}
          className="mb-2 flex min-h-[44px] items-center rounded-md px-3 text-xs font-semibold text-sidebar-muted hover:bg-white/10 hover:text-sidebar-text"
        >
          Lihat Harga Publik
        </Link>
        <Button
          variant="outline"
          size="md"
          fullWidth
          isLoading={loggingOut}
          onClick={() => void handleLogout()}
          leadingIcon={<LogOut aria-hidden="true" className="h-4 w-4" />}
          className="border-white/25 bg-transparent text-sidebar-text hover:bg-white/10"
        >
          Keluar Sesi
        </Button>
      </div>
    </aside>
  );

  return (
    <>
      <div className="hidden lg:fixed lg:inset-y-0 lg:left-0 lg:z-30 lg:block lg:w-64">
        {sidebarContent}
      </div>

      {mobileOpen ? (
        <div className="fixed inset-0 z-50 flex lg:hidden" role="dialog" aria-modal="true" aria-label="Menu Portal Internal">
          <div
            className="fixed inset-0 bg-ink-primary/50"
            aria-hidden="true"
            onClick={onCloseMobile}
          />
          <div className="relative z-10 h-full">{sidebarContent}</div>
        </div>
      ) : null}
    </>
  );
}
