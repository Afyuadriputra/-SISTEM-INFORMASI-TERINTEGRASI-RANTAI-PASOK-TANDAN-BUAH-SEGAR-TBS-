import type { ReactNode } from 'react';

export interface PageHeaderProps {
  readonly eyebrow?: string;
  readonly title: string;
  readonly description?: string;
  readonly actions?: ReactNode;
}

export function PageHeader({ eyebrow, title, description, actions }: PageHeaderProps) {
  return (
    <div className="flex flex-col gap-4 border-b border-border-subtle pb-5 sm:flex-row sm:items-end sm:justify-between">
      <div className="min-w-0 space-y-1">
        {eyebrow ? (
          <p className="font-mono text-xs font-semibold uppercase tracking-wide text-primary-default">
            {eyebrow}
          </p>
        ) : null}
        <h1 className="text-2xl font-bold tracking-tight text-ink-primary sm:text-[26px]">
          {title}
        </h1>
        {description ? (
          <p className="max-w-3xl text-sm text-ink-secondary">{description}</p>
        ) : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
    </div>
  );
}
