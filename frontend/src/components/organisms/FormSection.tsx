import type { ReactNode } from 'react';

export interface FormSectionProps {
  readonly stepNumber?: string;
  readonly title: string;
  readonly description?: string;
  readonly children: ReactNode;
  readonly aside?: ReactNode;
}

export function FormSection({
  stepNumber,
  title,
  description,
  children,
  aside,
}: FormSectionProps) {
  return (
    <section className="rounded-lg border border-border-subtle bg-surface-default p-5 sm:p-6">
      <div className="flex flex-col gap-2 border-b border-border-subtle pb-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            {stepNumber ? (
              <span className="inline-flex h-6 min-w-6 shrink-0 whitespace-nowrap items-center justify-center rounded bg-primary-subtle px-2 font-mono text-xs font-bold text-primary-default">
                {stepNumber}
              </span>
            ) : null}
            <h2 className="text-base font-bold text-ink-primary">{title}</h2>
          </div>
          {description ? <p className="mt-1 text-xs text-ink-secondary">{description}</p> : null}
        </div>
        {aside}
      </div>
      <div className="mt-4 space-y-4">{children}</div>
    </section>
  );
}
