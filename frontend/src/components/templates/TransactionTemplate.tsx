import type { ReactNode } from 'react';
import { PageHeader, type PageHeaderProps } from '@/components/organisms';
import type { AuthenticatedUser } from '@/lib/auth/permissions';
import { InternalAppShell } from './InternalAppShell';

export interface TransactionTemplateProps {
  readonly user: AuthenticatedUser;
  readonly header: PageHeaderProps;
  readonly noticeSlot?: ReactNode;
  readonly primarySlot: ReactNode;
  readonly secondarySlot?: ReactNode;
}

export function TransactionTemplate({
  user,
  header,
  noticeSlot,
  primarySlot,
  secondarySlot,
}: TransactionTemplateProps) {
  return (
    <InternalAppShell user={user}>
      <div className="space-y-6">
        <PageHeader {...header} />
        {noticeSlot}
        <div
          className={
            secondarySlot
              ? 'grid grid-cols-1 gap-6 xl:grid-cols-12'
              : 'space-y-6'
          }
        >
          <div className={secondarySlot ? 'min-w-0 space-y-6 xl:col-span-7' : 'min-w-0 space-y-6'}>
            {primarySlot}
          </div>
          {secondarySlot ? (
            <div className="min-w-0 space-y-6 xl:col-span-5">{secondarySlot}</div>
          ) : null}
        </div>
      </div>
    </InternalAppShell>
  );
}
