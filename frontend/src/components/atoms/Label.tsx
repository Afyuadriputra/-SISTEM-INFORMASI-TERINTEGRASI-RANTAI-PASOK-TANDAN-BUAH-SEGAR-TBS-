import type { LabelHTMLAttributes } from 'react';
import { cn } from './cn';

export interface LabelProps extends LabelHTMLAttributes<HTMLLabelElement> {
  readonly required?: boolean;
}

export function Label({ required = false, className, children, ...props }: LabelProps) {
  return (
    <label
      className={cn('inline-block text-sm font-semibold text-ink-primary', className)}
      {...props}
    >
      {children}
      {required ? (
        <span aria-hidden="true" className="ml-1 text-danger-solid">
          *
        </span>
      ) : null}
    </label>
  );
}
