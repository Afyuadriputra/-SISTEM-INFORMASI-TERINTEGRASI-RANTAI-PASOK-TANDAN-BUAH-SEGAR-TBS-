import { cn } from './cn';

export interface SkeletonRowProps {
  readonly lines?: number;
  readonly className?: string;
}

export function SkeletonRow({ lines = 3, className }: SkeletonRowProps) {
  return (
    <div aria-hidden="true" className={cn('space-y-2.5', className)}>
      {Array.from({ length: lines }, (_, index) => (
        <div
          key={index}
          className={cn(
            'h-4 rounded bg-surface-subtle',
            index === 0 ? 'w-3/4' : index === lines - 1 ? 'w-1/2' : 'w-full',
          )}
        />
      ))}
    </div>
  );
}
