import { QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider, createMemoryHistory } from '@tanstack/react-router';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { createAppRouter } from '@/app/router/router';
import { loginWithCredentials } from '@/lib/auth/session';
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

describe('F6 Receiving, Weighing & Grading UI', () => {
  it('creates draft receipt, previews Decimal Netto, rejects Tara > Bruto, grades & validates', async () => {
    const user = userEvent.setup();
    await loginWithCredentials({
      username: 'sim_kop_op_01',
      password: MOCK_SIMULATION_PASSWORD,
    });

    renderRoute('/app/koperasi/penerimaan');

    expect(
      await screen.findByRole(
        'heading',
        { name: /Pencatatan Penerimaan & Penimbangan TBS/i },
        { timeout: 5000 },
      ),
    ).toBeInTheDocument();

    expect(await screen.findByText(/Aturan Simulasi Grading/i)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Buat Draf Penerimaan/i }));
    expect(await screen.findByText(/Timbang & Grading: RCP-2026-/i)).toBeInTheDocument();

    // Verify WeightInputGroup rejects Tara > Bruto
    const grossInput = screen.getByLabelText(/Berat Bruto \(kg\)/i);
    const tareInput = screen.getByLabelText(/Berat Tara \(kg\)/i);
    await user.clear(grossInput);
    await user.type(grossInput, '1000');
    await user.clear(tareInput);
    await user.type(tareInput, '1500');
    expect(screen.getByText(/melebihi berat bruto/i)).toBeInTheDocument();

    // Valid weighing 5200.000 - 1200.000 = 4.000,000 kg
    await user.clear(grossInput);
    await user.type(grossInput, '5200');
    await user.clear(tareInput);
    await user.type(tareInput, '1200');
    expect(screen.getByText('4.000,000 kg')).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /Simpan Penimbangan/i }));
    await user.click(await screen.findByRole('button', { name: /Catat Grading Simulasi/i }));
    await user.click(screen.getByRole('button', { name: /Validasi Penerimaan/i }));

    expect((await screen.findAllByText('Tervalidasi')).length).toBeGreaterThan(0);
  });
});
