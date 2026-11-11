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

describe('F7 Contracts, Quota & Logistics e-DO UI', () => {
  it('blocks over-quota reservation cleanly with CONTRACT_QUOTA_EXCEEDED on /app/perumda/kontrak', async () => {
    const user = userEvent.setup();
    await loginWithCredentials({
      username: 'sim_perumda_ops_01',
      password: MOCK_SIMULATION_PASSWORD,
    });

    renderRoute('/app/perumda/kontrak');
    expect(
      await screen.findByRole(
        'heading',
        { name: /Manajemen Kontrak Niaga & Kuota Pasokan PKS/i },
        { timeout: 5000 },
      ),
    ).toBeInTheDocument();

    const reserveInput = await screen.findByLabelText(/Berat Dicadangkan \(kg\)/i);
    await user.clear(reserveInput);
    await user.type(reserveInput, '99999.000');
    await user.click(screen.getByRole('button', { name: /Cadangkan Kuota PKS/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(/CONTRACT_QUOTA_EXCEEDED/);
  });

  it('consolidates validated receipt into e-DO draft, prevents double allocation, and issues with QR token', async () => {
    const user = userEvent.setup();
    await logoutSession().catch(() => undefined);
    await loginWithCredentials({
      username: 'sim_kop_op_01',
      password: MOCK_SIMULATION_PASSWORD,
    });

    renderRoute('/app/koperasi/surat-jalan');
    expect(
      await screen.findByRole(
        'heading',
        { name: /Penyusunan & Penerbitan e-DO Konsolidasi/i },
        { timeout: 5000 },
      ),
    ).toBeInTheDocument();

    // Select the validated unallocated receipt RCV-2026-1110-004
    const validatedLabel = await screen.findByText('RCV-2026-1110-004');
    await user.click(validatedLabel);

    await user.click(screen.getByRole('button', { name: /Susun Draf e-DO/i }));
    expect((await screen.findAllByText(/EDO-2026-0106/)).length).toBeGreaterThan(0);

    // Double allocation attempt on the already locked receipt fails with LOG_DELIVERY_ALREADY_ASSIGNED
    await user.click(validatedLabel);
    await user.click(screen.getByRole('button', { name: /Susun Draf e-DO/i }));
    expect(await screen.findByRole('alert')).toHaveTextContent(/LOG_DELIVERY_ALREADY_ASSIGNED/);

    // Issue the drafted e-DO -> READY
    const issueButtons = screen.getAllByRole('button', { name: /Terbitkan e-DO/i });
    await user.click(issueButtons[0]);
    expect((await screen.findAllByText(/Siap Kirim/i)).length).toBeGreaterThan(0);
  });
});
