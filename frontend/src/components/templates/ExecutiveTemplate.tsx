import type { ReactNode } from 'react';
import { PageHeader, type PageHeaderProps } from '@/components/organisms';
import type { AuthenticatedUser } from '@/lib/auth/permissions';
import { InternalAppShell } from './InternalAppShell';

export interface ExecutiveTemplateProps {
  readonly user: AuthenticatedUser;
  readonly header: PageHeaderProps;
  readonly filterSlot?: ReactNode;
  readonly noticeSlot?: ReactNode;
  readonly kpiSlot?: ReactNode;
  readonly children: ReactNode;
}

export function ExecutiveTemplate({
  user,
  header,
  filterSlot,
  noticeSlot,
  kpiSlot,
  children,
}: ExecutiveTemplateProps) {
  return (
    <InternalAppShell user={user}>
      <div className="space-y-6">
        <PageHeader {...header} />
        {filterSlot}
        {noticeSlot}
        {kpiSlot}
        <div className="min-w-0 space-y-6">{children}</div>
      </div>
    </InternalAppShell>
  );
}
