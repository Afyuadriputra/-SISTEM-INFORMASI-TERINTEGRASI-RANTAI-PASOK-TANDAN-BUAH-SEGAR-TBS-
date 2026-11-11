import { forwardRef, type TextareaHTMLAttributes } from 'react';
import { cn } from './cn';

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  readonly hasError?: boolean;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  { hasError = false, className, rows = 3, ...props },
  ref,
) {
  return (
    <textarea
      ref={ref}
      rows={rows}
      aria-invalid={hasError || undefined}
      className={cn(
        'w-full rounded-md border bg-surface-default px-3 py-2.5 text-sm text-ink-primary placeholder:text-text-muted transition-colors duration-150 focus:border-primary-default focus:outline-none disabled:cursor-not-allowed disabled:bg-surface-subtle disabled:text-text-muted',
        hasError ? 'border-danger-solid bg-danger-bg/20' : 'border-border-control',
        className,
      )}
      {...props}
    />
  );
});
