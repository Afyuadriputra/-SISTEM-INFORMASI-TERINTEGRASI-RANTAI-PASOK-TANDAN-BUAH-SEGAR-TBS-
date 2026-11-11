import { QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider, createMemoryHistory } from '@tanstack/react-router';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { createAppRouter } from '@/app/router/router';
import { loginWithCredentials, logoutSession } from '@/lib/auth/session';
import { appQueryClient } from '@/lib/query/queryClient';
import { MOCK_SIMULATION_PASSWORD } from '@/mocks/mockDb';

function renderRoute(initialPath: string) {
  cleanup();
  const history = createMemoryHistory({ initialEntries: [initialPath] });
  const router = createAppRouter(history);
  return render(
    <QueryClientProvider client={appQueryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  );
}

describe('F8 Mill Weighing & Reconciliation UI', () => {
  it('enforces cross-mill isolation (MILL_EDO_MILL_MISMATCH) and creates + verifies mill ticket', async () => {
    const user = userEvent.setup();
    await loginWithCredentials({
      username: 'sim_mill_op_02',
      password: MOCK_SIMULATION_PASSWORD,
    });

    renderRoute('/app/pks');
    expect(
      await screen.findByRole(
        'heading',
        { name: /Dashboard & Verifikasi Kedatangan TBS PKS/i },
        { timeout: 5000 },
      ),
    ).toBeInTheDocument();

    // Operator for PKS-02 trying to verify PKS-01's e-DO fails cleanly
    await user.type(screen.getByLabelText(/Token QR \/ Nomor e-DO/i), 'EDO-2026-1110-043');
    await user.click(screen.getByRole('button', { name: /Verifikasi Tiba/i }));
    expect(await screen.findByRole('alert')).toHaveTextContent(/MILL_EDO_MILL_MISMATCH/);

    // Switch to authorized PKS-01 operator
    await logoutSession();
    await loginWithCredentials({
      username: 'sim_mill_op_01',
      password: MOCK_SIMULATION_PASSWORD,
    });

    renderRoute('/app/pks/tiket-timbang');
    expect(
      await screen.findByRole(
        'heading',
        { name: /Pencatatan Tiket Jembatan Timbang PKS/i },
        { timeout: 5000 },
      ),
    ).toBeInTheDocument();

    const edoOpt = (await screen.findByRole('option', {
      name: /EDO-2026-1110-043/,
    })) as HTMLOptionElement;
    await user.selectOptions(screen.getByLabelText(/Surat Jalan e-DO/i), edoOpt.value);
    await user.type(screen.getByLabelText(/Nomor Tiket Timbang PKS/i), 'WB-PKC-2026-9955');
    await user.click(screen.getByRole('button', { name: /Simpan Tiket Timbang PKS/i }));
    expect(await screen.findByText('WB-PKC-2026-9955')).toBeInTheDocument();

    const verifyButtons = screen.getAllByRole('button', { name: /Verifikasi Final/i });
    await user.click(verifyButtons[0]);
    expect((await screen.findAllByText('Terverifikasi')).length).toBeGreaterThan(0);
  });

  it('displays negative diff anomaly, runs simulation allocation, and blocks FINAL allocation (Pending SOP)', async () => {
    const user = userEvent.setup();
    await logoutSession().catch(() => undefined);
    await loginWithCredentials({
      username: 'sim_perumda_ops_01',
      password: MOCK_SIMULATION_PASSWORD,
    });

    renderRoute('/app/perumda/rekonsiliasi');
    expect(
      await screen.findByRole(
        'heading',
        { name: /Rekonsiliasi Selisih Berat Koperasi vs PKS/i },
        { timeout: 5000 },
      ),
    ).toBeInTheDocument();

    expect((await screen.findAllByText(/Anomali Selisih Negatif/i)).length).toBeGreaterThan(0);

    // Simulation mode runs cleanly
    const simButton = await screen.findByRole('button', { name: /Jalankan Simulasi Alokasi/i });
    await user.click(simButton);
    expect((await screen.findAllByText(/SIMULATION_ONLY/)).length).toBeGreaterThan(0);

    // Final mode must surface REC_ALLOCATION_POLICY_UNCONFIRMED cleanly
    await user.click(screen.getByRole('button', { name: /Uji Finalisasi Alokasi Resmi/i }));
    expect(await screen.findByRole('alert')).toHaveTextContent(
      /REC_ALLOCATION_POLICY_UNCONFIRMED/,
    );
  });
});
