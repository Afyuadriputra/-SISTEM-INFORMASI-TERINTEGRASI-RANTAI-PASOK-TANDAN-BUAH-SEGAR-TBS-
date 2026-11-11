import { Badge } from '@/components/atoms';
import { resolveStatusAppearance } from './statusMeta';

export interface StatusIndicatorProps {
  readonly status: string;
  readonly labelOverride?: string;
  readonly className?: string;
}

export function StatusIndicator({ status, labelOverride, className }: StatusIndicatorProps) {
  const appearance = resolveStatusAppearance(status);
  return (
    <Badge tone={appearance.tone} className={className}>
      {labelOverride ?? appearance.label}
    </Badge>
  );
}
