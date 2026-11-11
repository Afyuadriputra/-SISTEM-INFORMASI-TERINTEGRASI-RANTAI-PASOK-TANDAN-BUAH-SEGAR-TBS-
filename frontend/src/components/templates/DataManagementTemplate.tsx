import type { ReactNode } from 'react';
import { PageHeader, type PageHeaderProps } from '@/components/organisms';
import type { AuthenticatedUser } from '@/lib/auth/permissions';
import { InternalAppShell } from './InternalAppShell';

export interface DataManagementTemplateProps {
  readonly user: AuthenticatedUser;
  readonly header: PageHeaderProps;
  readonly noticeSlot?: ReactNode;
  readonly filterSlot?: ReactNode;
  readonly formSlot?: ReactNode;
  readonly children: ReactNode;
}

export function DataManagementTemplate({
  user,
  header,
  noticeSlot,
  filterSlot,
  formSlot,
  children,
}: DataManagementTemplateProps) {
  return (
    <InternalAppShell user={user}>
      <div className="space-y-6">
        <PageHeader {...header} />
        {noticeSlot}
        {filterSlot}
        {formSlot}
        <div className="min-w-0 space-y-6">{children}</div>
      </div>
    </InternalAppShell>
  );
}
