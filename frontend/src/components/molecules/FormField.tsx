import type { ReactNode } from 'react';
import { Label } from '@/components/atoms';

export interface FormFieldProps {
  readonly id: string;
  readonly label: string;
  readonly required?: boolean;
  readonly helperText?: string;
  readonly error?: string;
  readonly children: ReactNode;
}

export function FormField({
  id,
  label,
  required = false,
  helperText,
  error,
  children,
}: FormFieldProps) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={id} required={required}>
        {label}
      </Label>
      {children}
      {error ? (
        <p id={`${id}-error`} role="alert" className="text-xs font-medium text-danger-text">
          {error}
        </p>
      ) : helperText ? (
        <p id={`${id}-hint`} className="text-xs text-ink-secondary">
          {helperText}
        </p>
      ) : null}
    </div>
  );
}
