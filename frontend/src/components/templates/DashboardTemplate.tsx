import type { ReactNode } from 'react';
import { PageHeader, type PageHeaderProps } from '@/components/organisms';
import type { AuthenticatedUser } from '@/lib/auth/permissions';
import { InternalAppShell } from './InternalAppShell';

export interface DashboardTemplateProps {
  readonly user: AuthenticatedUser;
  readonly header: PageHeaderProps;
  readonly noticeSlot?: ReactNode;
  readonly kpiSlot?: ReactNode;
  readonly children: ReactNode;
}

export function DashboardTemplate({
  user,
  header,
  noticeSlot,
  kpiSlot,
  children,
}: DashboardTemplateProps) {
  return (
    <InternalAppShell user={user}>
      <div className="space-y-6">
        <PageHeader {...header} />
        {noticeSlot}
        {kpiSlot}
        <div className="space-y-6">{children}</div>
      </div>
    </InternalAppShell>
  );
}
