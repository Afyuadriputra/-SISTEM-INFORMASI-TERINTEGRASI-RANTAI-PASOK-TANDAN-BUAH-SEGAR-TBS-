import type { ReactNode } from 'react';
import { DemoModeBanner } from '@/components/molecules';
import { PublicFooter, PublicNavbar } from '@/components/organisms';

export interface PublicTemplateProps {
  readonly children: ReactNode;
  readonly fullBleedTop?: ReactNode;
}

export function PublicTemplate({ children, fullBleedTop }: PublicTemplateProps) {
  return (
    <div className="flex min-h-screen flex-col bg-canvas">
      <DemoModeBanner variant="bar" />
      <PublicNavbar />
      {fullBleedTop}
      <main id="main-content" className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 sm:px-6">
        {children}
      </main>
      <PublicFooter />
    </div>
  );
}
