import { Link } from '@tanstack/react-router';
import { ArrowLeft, Sprout } from 'lucide-react';
import type { ReactNode } from 'react';

export interface AuthTemplateProps {
  readonly children: ReactNode;
}

export function AuthTemplate({ children }: AuthTemplateProps) {
  return (
    <div className="flex min-h-screen flex-col justify-between bg-canvas px-4 py-6 sm:px-6">
      <div className="mx-auto flex w-full max-w-5xl items-center justify-between">
        <Link
          to="/"
          className="inline-flex min-h-[44px] items-center gap-2 text-sm font-semibold text-primary-default hover:text-brand-hover"
        >
          <ArrowLeft aria-hidden="true" className="h-4 w-4" />
          <span>Kembali ke Portal Publik</span>
        </Link>
        <div className="flex items-center gap-2 text-sm font-bold text-ink-primary">
          <Sprout aria-hidden="true" className="h-4 w-4 text-primary-default" />
          <span>Perumda Tuah Sekata</span>
        </div>
      </div>

      <main id="main-content" className="mx-auto my-8 w-full max-w-5xl">
        {children}
      </main>

      <p className="text-center text-xs text-text-muted">
        Portal Internal Terbatas Unit Agro Niaga | Akses dicatat pada audit log keamanan.
      </p>
    </div>
  );
}
