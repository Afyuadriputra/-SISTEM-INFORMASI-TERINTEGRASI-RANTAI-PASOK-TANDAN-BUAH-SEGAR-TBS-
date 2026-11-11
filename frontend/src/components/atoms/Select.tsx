import { forwardRef, type SelectHTMLAttributes } from 'react';
import { cn } from './cn';

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  readonly hasError?: boolean;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { hasError = false, className, children, ...props },
  ref,
) {
  return (
    <select
      ref={ref}
      aria-invalid={hasError || undefined}
      className={cn(
        'w-full min-h-[44px] rounded-md border bg-surface-default px-3 py-2 text-sm text-ink-primary transition-colors duration-150 focus:border-primary-default focus:outline-none disabled:cursor-not-allowed disabled:bg-surface-subtle disabled:text-text-muted',
        hasError ? 'border-danger-solid bg-danger-bg/20' : 'border-border-control',
        className,
      )}
      {...props}
    >
      {children}
    </select>
  );
});
