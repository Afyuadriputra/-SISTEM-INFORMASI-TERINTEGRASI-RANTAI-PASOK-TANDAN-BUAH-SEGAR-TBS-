import { useEffect, useId, useState } from 'react';
import { Button, Textarea } from '@/components/atoms';
import { FormField } from '@/components/molecules';

export interface ConfirmDialogProps {
  readonly open: boolean;
  readonly title: string;
  readonly description: string;
  readonly confirmLabel?: string;
  readonly cancelLabel?: string;
  readonly tone?: 'primary' | 'danger';
  readonly requireReason?: boolean;
  readonly reasonLabel?: string;
  readonly reasonPlaceholder?: string;
  readonly isSubmitting?: boolean;
  readonly onConfirm: (reason: string) => void | Promise<void>;
  readonly onCancel: () => void;
}

function ConfirmDialogBody({
  title,
  description,
  confirmLabel = 'Konfirmasi',
  cancelLabel = 'Batal',
  tone = 'primary',
  requireReason = false,
  reasonLabel = 'Alasan Tindakan',
  reasonPlaceholder = 'Tuliskan alasan atau referensi dokumen...',
  isSubmitting = false,
  onConfirm,
  onCancel,
}: Omit<ConfirmDialogProps, 'open'>) {
  const titleId = useId();
  const [reason, setReason] = useState('');
  const [reasonError, setReasonError] = useState<string | undefined>(undefined);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !isSubmitting) {
        onCancel();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isSubmitting, onCancel]);

  const handleConfirmClick = () => {
    const trimmed = reason.trim();
    if (requireReason && trimmed.length < 5) {
      setReasonError('Alasan wajib diisi minimal 5 karakter untuk jejak audit.');
      return;
    }
    setReasonError(undefined);
    void onConfirm(trimmed);
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
      className="fixed inset-0 z-50 flex items-center justify-center bg-ink-primary/55 p-4"
    >
      <div className="w-full max-w-md rounded-lg border border-border-subtle bg-surface-default p-6 shadow-lg">
        <h2 id={titleId} className="text-lg font-bold text-ink-primary">
          {title}
        </h2>
        <p className="mt-2 text-sm leading-relaxed text-ink-secondary">{description}</p>

        {requireReason ? (
          <div className="mt-4">
            <FormField id="confirm-dialog-reason" label={reasonLabel} required error={reasonError}>
              <Textarea
                id="confirm-dialog-reason"
                value={reason}
                hasError={Boolean(reasonError)}
                placeholder={reasonPlaceholder}
                onChange={(e) => {
                  setReason(e.target.value);
                  if (reasonError) {
                    setReasonError(undefined);
                  }
                }}
              />
            </FormField>
          </div>
        ) : null}

        <div className="mt-6 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
          <Button variant="outline" disabled={isSubmitting} onClick={onCancel}>
            {cancelLabel}
          </Button>
          <Button
            variant={tone === 'danger' ? 'danger' : 'primary'}
            isLoading={isSubmitting}
            onClick={handleConfirmClick}
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}

export function ConfirmDialog({ open, ...rest }: ConfirmDialogProps) {
  if (!open) {
    return null;
  }
  return <ConfirmDialogBody {...rest} />;
}
