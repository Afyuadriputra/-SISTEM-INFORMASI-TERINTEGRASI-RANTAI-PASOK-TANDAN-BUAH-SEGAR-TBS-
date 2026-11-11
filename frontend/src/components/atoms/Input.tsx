import { forwardRef, type InputHTMLAttributes } from 'react';
import { cn } from './cn';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  readonly hasError?: boolean;
  readonly monospace?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { hasError = false, monospace = false, className, ...props },
  ref,
) {
  return (
    <input
      ref={ref}
      aria-invalid={hasError || undefined}
      className={cn(
        'w-full min-h-[44px] rounded-md border bg-surface-default px-3 py-2 text-sm text-ink-primary placeholder:text-text-muted transition-colors duration-150 focus:border-primary-default focus:outline-none disabled:cursor-not-allowed disabled:bg-surface-subtle disabled:text-text-muted',
        hasError ? 'border-danger-solid bg-danger-bg/20' : 'border-border-control',
        monospace && 'font-mono tabular-nums',
        className,
      )}
      {...props}
    />
  );
});
