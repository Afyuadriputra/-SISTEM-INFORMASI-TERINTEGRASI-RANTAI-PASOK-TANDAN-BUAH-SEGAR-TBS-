import { Link, useRouterState } from '@tanstack/react-router';
import { Menu, Sprout, X } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { cn } from '@/components/atoms';
import { PUBLIC_NAV_ITEMS } from './navigationConfig';

export function PublicNavbar() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const menuBtnRef = useRef<HTMLButtonElement>(null);
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  useEffect(() => {
    if (!mobileOpen) {
      return;
    }
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setMobileOpen(false);
        requestAnimationFrame(() => menuBtnRef.current?.focus());
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [mobileOpen]);

  return (
    <header className="sticky top-0 z-40 border-b border-border-subtle bg-surface-default/95 backdrop-blur-xs">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
        <Link to="/" activeOptions={{ exact: true }} className="flex min-w-0 items-center gap-2.5 text-ink-primary no-underline">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-primary-default text-primary-foreground">
            <Sprout aria-hidden="true" className="h-5 w-5" />
          </span>
          <span className="min-w-0">
            <span className="block truncate text-sm font-bold leading-tight text-ink-primary">
              Perumda Tuah Sekata
            </span>
            <span className="block truncate text-xs font-medium text-primary-default">
              Unit Agro Niaga TBS
            </span>
          </span>
        </Link>

        <nav aria-label="Navigasi Portal Publik" className="hidden items-center gap-1 lg:flex">
          {PUBLIC_NAV_ITEMS.map((item) => {
            const active =
              item.to === '/'
                ? pathname === '/'
                : pathname === item.to || pathname.startsWith(`${item.to}/`);
            return (
              <Link
                key={item.to}
                to={item.to}
                activeOptions={{ exact: item.to === '/' }}
                aria-current={active ? 'page' : undefined}
                className={cn(
                  'inline-flex min-h-[44px] items-center rounded-md px-3 text-sm font-semibold transition-colors',
                  active
                    ? 'bg-primary-subtle text-primary-default'
                    : 'text-ink-secondary hover:bg-surface-subtle hover:text-ink-primary',
                )}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          <Link
            to="/login"
            className="hidden min-h-[44px] items-center rounded-md bg-primary-default px-4 text-sm font-semibold text-primary-foreground transition-colors hover:bg-brand-hover lg:inline-flex"
          >
            Masuk Portal Internal
          </Link>
          <button
            ref={menuBtnRef}
            type="button"
            aria-expanded={mobileOpen}
            aria-controls="public-mobile-drawer"
            aria-label={mobileOpen ? 'Tutup menu navigasi' : 'Buka menu navigasi'}
            onClick={() => setMobileOpen((prev) => !prev)}
            className="inline-flex h-11 w-11 items-center justify-center rounded-md border border-border-control bg-surface-default text-ink-primary lg:hidden"
          >
            {mobileOpen ? <X aria-hidden="true" className="h-5 w-5" /> : <Menu aria-hidden="true" className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {mobileOpen ? (
        <div
          id="public-mobile-drawer"
          className="border-t border-border-subtle bg-surface-default px-4 py-3 lg:hidden"
        >
          <nav aria-label="Menu Mobile Portal Publik" className="flex flex-col gap-1">
            {PUBLIC_NAV_ITEMS.map((item) => {
              const active =
                item.to === '/'
                  ? pathname === '/'
                  : pathname === item.to || pathname.startsWith(`${item.to}/`);
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  activeOptions={{ exact: item.to === '/' }}
                  onClick={() => setMobileOpen(false)}
                  aria-current={active ? 'page' : undefined}
                  className={cn(
                    'flex min-h-[44px] items-center rounded-md px-3 text-sm font-semibold',
                    active
                      ? 'bg-primary-subtle text-primary-default'
                      : 'text-ink-secondary hover:bg-surface-subtle hover:text-ink-primary',
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
            <Link
              to="/login"
              onClick={() => setMobileOpen(false)}
              className="mt-2 flex min-h-[44px] items-center justify-center rounded-md bg-primary-default px-4 text-sm font-semibold text-primary-foreground hover:bg-brand-hover"
            >
              Masuk Portal Internal
            </Link>
          </nav>
        </div>
      ) : null}
    </header>
  );
}
