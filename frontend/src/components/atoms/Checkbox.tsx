import { forwardRef, type InputHTMLAttributes } from 'react';
import { cn } from './cn';

export interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  readonly label: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(function Checkbox(
  { label, id, className, ...props },
  ref,
) {
  return (
    <label
      htmlFor={id}
      className={cn(
        'inline-flex min-h-[44px] cursor-pointer items-center gap-2.5 text-sm text-ink-primary select-none',
        props.disabled && 'cursor-not-allowed text-text-muted',
        className,
      )}
    >
      <input
        ref={ref}
        id={id}
        type="checkbox"
        className="h-4 w-4 rounded border-border-control text-primary-default accent-primary-default focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-default"
        {...props}
      />
      <span>{label}</span>
    </label>
  );
});
