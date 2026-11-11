import { StatusIndicator } from '@/components/molecules';
import { formatWibDateTime } from '@/lib/decimal/precision';

export interface TimelineEventItem {
  readonly id: string;
  readonly status: string;
  readonly timestamp: string;
  readonly actor?: string | null;
  readonly note?: string | null;
}

export interface StatusTimelineProps {
  readonly events: readonly TimelineEventItem[];
  readonly emptyMessage?: string;
}

export function StatusTimeline({
  events,
  emptyMessage = 'Belum ada riwayat perubahan status.',
}: StatusTimelineProps) {
  if (events.length === 0) {
    return <p className="text-xs text-text-muted">{emptyMessage}</p>;
  }

  return (
    <ol className="space-y-3 border-l-2 border-border-subtle pl-4">
      {events.map((event) => (
        <li key={event.id} className="relative space-y-1">
          <span
            aria-hidden="true"
            className="absolute top-1.5 -left-[21px] h-2.5 w-2.5 rounded-full border-2 border-surface-default bg-primary-default"
          />
          <div className="flex flex-wrap items-center gap-2">
            <StatusIndicator status={event.status} />
            <span className="font-mono text-xs text-text-muted">
              {formatWibDateTime(event.timestamp)}
            </span>
          </div>
          {event.actor ? (
            <p className="text-xs font-medium text-ink-secondary">Petugas: {event.actor}</p>
          ) : null}
          {event.note ? <p className="text-xs text-ink-primary">{event.note}</p> : null}
        </li>
      ))}
    </ol>
  );
}
