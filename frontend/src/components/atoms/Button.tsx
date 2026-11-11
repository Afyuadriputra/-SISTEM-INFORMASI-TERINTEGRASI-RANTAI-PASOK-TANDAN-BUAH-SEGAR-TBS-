import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { Spinner } from './Spinner';
import { cn } from './cn';

export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  readonly variant?: ButtonVariant;
  readonly size?: ButtonSize;
  readonly isLoading?: boolean;
  readonly leadingIcon?: ReactNode;
  readonly fullWidth?: boolean;
}

const VARIANT_CLASSES: Record<ButtonVariant, string> = {
  primary:
    'bg-primary-default text-primary-foreground hover:bg-brand-hover border border-primary-default disabled:opacity-55',
  secondary:
    'bg-secondary-default text-secondary-foreground hover:bg-primary-default border border-secondary-default disabled:opacity-55',
  outline:
    'bg-surface-default text-ink-primary border border-border-control hover:bg-surface-subtle disabled:opacity-55',
  ghost:
    'bg-transparent text-ink-primary border border-transparent hover:bg-surface-subtle disabled:opacity-55',
  danger:
    'bg-danger-solid text-white border border-danger-solid hover:bg-danger-text disabled:opacity-55',
};

const SIZE_CLASSES: Record<ButtonSize, string> = {
  sm: 'min-h-[44px] px-3 py-2 text-xs',
  md: 'min-h-[44px] px-4 py-2.5 text-sm',
  lg: 'min-h-[48px] px-6 py-3 text-base',
};

export function Button({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leadingIcon,
  fullWidth = false,
  disabled,
  className,
  children,
  type = 'button',
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      disabled={disabled || isLoading}
      aria-busy={isLoading || undefined}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-md font-semibold transition-colors duration-150 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-default disabled:cursor-not-allowed',
        VARIANT_CLASSES[variant],
        SIZE_CLASSES[size],
        fullWidth && 'w-full',
        className,
      )}
      {...props}
    >
      {isLoading ? <Spinner size="sm" /> : leadingIcon}
      <span>{children}</span>
    </button>
  );
}
