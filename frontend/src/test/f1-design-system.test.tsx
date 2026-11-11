import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { Button, Input } from '@/components/atoms';
import {
  DateRangeFilter,
  LocationLink,
  PolicyNoticeBanner,
  StatusIndicator,
  WeightInputGroup,
} from '@/components/molecules';
import {
  ConfirmDialog,
  DataTable,
  StateFeedbackCard,
  StatusTimeline,
} from '@/components/organisms';
import { ApiError } from '@/lib/errors/errorCatalog';

describe('F1 Design System: Atoms, Molecules & Organisms', () => {
  it('renders Button loading state and Input accessible error attribute', () => {
    render(
      <div>
        <Button isLoading>Menyimpan</Button>
        <Input aria-label="Berat" hasError value="abc" onChange={() => undefined} />
      </div>,
    );

    const btn = screen.getByRole('button', { name: /Menyimpan/i });
    expect(btn).toBeDisabled();
    expect(btn).toHaveAttribute('aria-busy', 'true');
    expect(screen.getByLabelText('Berat')).toHaveAttribute('aria-invalid', 'true');
  });

  it('computes real-time Netto preview in WeightInputGroup and flags Tara > Bruto', async () => {
    const user = userEvent.setup();
    let gross = '4200.500';
    let tare = '1500.250';
    const { rerender } = render(
      <WeightInputGroup
        grossValue={gross}
        tareValue={tare}
        onGrossChange={(v) => {
          gross = v;
        }}
        onTareChange={(v) => {
          tare = v;
        }}
      />,
    );

    expect(screen.getByText('2.700,250 kg')).toBeInTheDocument();
    expect(screen.getByText(/BR-TBS-004/)).toBeInTheDocument();

    rerender(
      <WeightInputGroup
        grossValue="1000"
        tareValue="1200"
        onGrossChange={vi.fn()}
        onTareChange={vi.fn()}
      />,
    );
    expect(screen.getByText(/melebihi berat bruto/i)).toBeInTheDocument();
    await user.tab();
  });

  it('renders StatusIndicator and LocationLink honestly without synthetic coordinates', () => {
    render(
      <div>
        <StatusIndicator status="DISPUTE_HOLD" />
        <StatusIndicator status="SIMULATION_ONLY" />
        <LocationLink
          address="Jl. Lintas Timur KM 18"
          district="Bandar Seikijang"
          regency="Pelalawan"
          latitude={null}
          longitude={null}
          hasVerifiedCoordinates={false}
        />
        <DateRangeFilter
          fromDate="2026-11-12"
          toDate="2026-11-10"
          onFromChange={vi.fn()}
          onToChange={vi.fn()}
        />
        <PolicyNoticeBanner
          kind="pending_sop"
          title="Menunggu Pengesahan SOP"
          description="Aturan alokasi menggunakan mode simulasi."
        />
      </div>,
    );

    expect(screen.getByText('Ditahan Sengketa')).toBeInTheDocument();
    expect(screen.getByText('Aturan Simulasi')).toBeInTheDocument();
    expect(screen.getByText(/tanpa pin perkiraan/i)).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveTextContent(/tidak boleh mendahului/i);
  });

  it('handles ConfirmDialog keyboard Escape and mandatory reason check', async () => {
    const user = userEvent.setup();
    const onConfirm = vi.fn();
    const onCancel = vi.fn();

    render(
      <ConfirmDialog
        open
        title="Tolak Harga PKS"
        description="Tindakan ini akan mengembalikan kutipan ke penyusun."
        requireReason
        onConfirm={onConfirm}
        onCancel={onCancel}
      />,
    );

    await user.click(screen.getByRole('button', { name: 'Konfirmasi' }));
    expect(screen.getByRole('alert')).toHaveTextContent(/minimal 5 karakter/i);
    expect(onConfirm).not.toHaveBeenCalled();

    await user.type(screen.getByLabelText(/Alasan Tindakan/i), 'Bukti dokumen kurang jelas');
    await user.click(screen.getByRole('button', { name: 'Konfirmasi' }));
    expect(onConfirm).toHaveBeenCalledWith('Bukti dokumen kurang jelas');

    await user.keyboard('{Escape}');
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it('renders DataTable, StatusTimeline, and StateFeedbackCard with Request ID', () => {
    const err = new ApiError({
      status: 409,
      code: 'FIN_POLICY_UNCONFIRMED',
      requestId: 'req-f1-0099',
    });

    render(
      <div>
        <DataTable
          caption="Daftar Uji"
          rows={[{ id: '1', name: 'PKS Lembah Subur' }]}
          getRowKey={(r) => r.id}
          columns={[{ key: 'name', header: 'Nama PKS', render: (r) => r.name }]}
        />
        <StatusTimeline
          events={[
            {
              id: 'ev1',
              status: 'VERIFIED',
              timestamp: '2026-11-10T03:00:00Z',
              actor: 'Staf Operasional',
              note: 'Data sesuai bukti.',
            },
          ]}
        />
        <StateFeedbackCard variant="error" error={err} onAction={vi.fn()} />
      </div>,
    );

    expect(screen.getByText('PKS Lembah Subur')).toBeInTheDocument();
    expect(screen.getByText(/Ref.*req-f1-0099|Request ID\): req-f1-0099/i)).toBeInTheDocument();
    expect(screen.getByText('Terverifikasi')).toBeInTheDocument();
  });
});
