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

describe('F5 Pricing Management (Maker != Checker & Disbun Separation)', () => {
  it('enforces Draft -> Submit -> SoD block for maker -> Checker Verify -> Publish', async () => {
    const user = userEvent.setup();
    await loginWithCredentials({
      username: 'sim_perumda_ops_01',
      password: MOCK_SIMULATION_PASSWORD,
    });

    renderRoute('/app/perumda/harga');

    expect(
      await screen.findByRole('heading', { name: /Manajemen Harga Multi-PKS & Acuan Disbun/i }, { timeout: 5000 }),
    ).toBeInTheDocument();

    const priceInput = await screen.findByLabelText(/Nominal \(Rp\/kg\)/i);
    await user.clear(priceInput);
    await user.type(priceInput, '2940.00');
    await user.click(screen.getByRole('button', { name: /Simpan Draf Harga PKS/i }));

    expect(await screen.findByText('Rp 2.940,00/kg')).toBeInTheDocument();

    // Submit newly created DRAFT
    const submitButtons = screen.getAllByRole('button', { name: /Ajukan Verifikasi/i });
    await user.click(submitButtons[0]);

    // Same maker trying self-verify triggers AUTH_CONFLICT_OF_DUTIES alert
    const selfVerifyButtons = await screen.findAllByRole('button', {
      name: /Uji Blokir Self-Verify/i,
    });
    await user.click(selfVerifyButtons[0]);
    expect(await screen.findByRole('alert')).toHaveTextContent(/AUTH_CONFLICT_OF_DUTIES/);

    // Switch to second Perumda Ops user (Checker)
    await logoutSession();
    await loginWithCredentials({
      username: 'sim_perumda_ops_02',
      password: MOCK_SIMULATION_PASSWORD,
    });

    renderRoute('/app/perumda/harga');
    const approveButtons = await screen.findAllByRole('button', {
      name: /Setujui Verifikasi/i,
    }, { timeout: 5000 });
    await user.click(approveButtons[0]);

    const publishButtons = await screen.findAllByRole('button', { name: /Publikasikan/i });
    await user.click(publishButtons[0]);
    expect((await screen.findAllByText('Dipublikasikan')).length).toBeGreaterThan(0);
  });
});
