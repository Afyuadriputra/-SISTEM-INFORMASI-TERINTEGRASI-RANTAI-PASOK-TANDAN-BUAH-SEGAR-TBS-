import type { HTMLAttributes } from 'react';
import { cn } from './cn';

export type BadgeTone = 'neutral' | 'primary' | 'success' | 'warning' | 'danger' | 'info';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  readonly tone?: BadgeTone;
}

const TONE_CLASSES: Record<BadgeTone, string> = {
  neutral: 'bg-neutral-bg text-neutral-text border-border-subtle',
  primary: 'bg-primary-subtle text-primary-default border-primary-default/20',
  success: 'bg-success-bg text-success-text border-success-text/20',
  warning: 'bg-warning-bg text-warning-text border-warning-text/20',
  danger: 'bg-danger-bg text-danger-text border-danger-text/20',
  info: 'bg-info-bg text-info-text border-info-text/20',
};

export function Badge({ tone = 'neutral', className, children, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-sm border px-2 py-0.5 text-xs font-semibold leading-5',
        TONE_CLASSES[tone],
        className,
      )}
      {...props}
    >
      {children}
    </span>
  );
}
