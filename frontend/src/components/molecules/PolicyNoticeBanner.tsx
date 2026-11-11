import { AlertTriangle, Info, ShieldAlert } from 'lucide-react';
import type { ReactNode } from 'react';
import { cn } from '@/components/atoms';

export type NoticeKind = 'simulation' | 'pending_sop' | 'non_approver' | 'info';

export interface PolicyNoticeBannerProps {
  readonly kind: NoticeKind;
  readonly title: string;
  readonly description: string;
  readonly footer?: ReactNode;
  readonly className?: string;
}

const STYLES: Record<NoticeKind, { wrapper: string; iconColor: string; Icon: typeof Info }> = {
  simulation: {
    wrapper: 'border-accent-default/35 bg-warning-bg text-warning-text',
    iconColor: 'text-accent-default',
    Icon: AlertTriangle,
  },
  pending_sop: {
    wrapper: 'border-accent-default/35 bg-accent-subtle text-accent-text',
    iconColor: 'text-accent-default',
    Icon: AlertTriangle,
  },
  non_approver: {
    wrapper: 'border-danger-text/30 bg-danger-bg text-danger-text',
    iconColor: 'text-danger-solid',
    Icon: ShieldAlert,
  },
  info: {
    wrapper: 'border-primary-default/25 bg-primary-subtle text-primary-default',
    iconColor: 'text-primary-default',
    Icon: Info,
  },
};

export function PolicyNoticeBanner({
  kind,
  title,
  description,
  footer,
  className,
}: PolicyNoticeBannerProps) {
  const cfg = STYLES[kind];
  const IconComp = cfg.Icon;
  return (
    <div
      role={kind === 'non_approver' ? 'alert' : 'note'}
      className={cn('rounded-lg border px-4 py-3 text-sm', cfg.wrapper, className)}
    >
      <div className="flex items-start gap-3">
        <IconComp aria-hidden="true" className={cn('mt-0.5 h-5 w-5 shrink-0', cfg.iconColor)} />
        <div className="space-y-1">
          <p className="font-semibold">{title}</p>
          <p className="text-xs leading-relaxed opacity-95">{description}</p>
          {footer ? <div className="pt-1 text-xs">{footer}</div> : null}
        </div>
      </div>
    </div>
  );
}
