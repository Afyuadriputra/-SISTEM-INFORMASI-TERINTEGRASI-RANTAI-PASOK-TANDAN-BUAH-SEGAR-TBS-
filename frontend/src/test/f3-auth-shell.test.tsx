import { QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider, createMemoryHistory } from '@tanstack/react-router';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { createAppRouter } from '@/app/router/router';
import { appQueryClient } from '@/lib/query/queryClient';
import { MOCK_SIMULATION_PASSWORD } from '@/mocks/mockDb';

function renderRoute(initialPath: string) {
  cleanup();
  const history = createMemoryHistory({ initialEntries: [initialPath] });
  const router = createAppRouter(history);
  return {
    history,
    ...render(
      <QueryClientProvider client={appQueryClient}>
        <RouterProvider router={router} />
      </QueryClientProvider>,
    ),
  };
}

describe('F3 Auth & Role App Shell', () => {
  it('redirects anonymous access to internal routes onto /login with next parameter', async () => {
    const { history } = renderRoute('/app/perumda');
    expect(
      await screen.findByRole(
        'heading',
        { name: /Masuk Sistem Rantai Pasok TBS/i },
        { timeout: 4000 },
      ),
    ).toBeInTheDocument();
    expect(history.location.pathname).toBe('/login');
  });

  it('logs in cleanly, rejects invalid password generically, and redirects authorized role', async () => {
    const user = userEvent.setup();
    const { history } = renderRoute('/login');

    await user.type(await screen.findByLabelText(/Username/i, {}, { timeout: 4000 }), 'sim_perumda_ops_01');
    await user.type(screen.getByLabelText(/^Kata Sandi/i), 'WrongPassword99');
    await user.click(screen.getByRole('button', { name: /Masuk ke Portal Internal/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(
      /Username atau kata sandi tidak sesuai/i,
    );

    const pwdInput = screen.getByLabelText(/^Kata Sandi/i);
    await user.clear(pwdInput);
    await user.type(pwdInput, MOCK_SIMULATION_PASSWORD);
    await user.click(screen.getByRole('button', { name: /Masuk ke Portal Internal/i }));

    await waitFor(() => {
      expect(history.location.pathname).toBe('/app/perumda');
    });
  });

  it('enforces cross-role RBAC 403 view when farmer accesses Perumda route', async () => {
    const user = userEvent.setup();
    renderRoute('/login');

    await user.click(await screen.findByText('sim_petani_01'));
    await user.click(screen.getByRole('button', { name: /Masuk ke Portal Internal/i }));
    await screen.findByRole('heading', { name: /Portal Transparansi Petani/i }, { timeout: 5000 });

    renderRoute('/app/perumda');
    expect(await screen.findByText(/AUTH_ACCESS_DENIED/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Kembali ke Beranda Peran/i })).toHaveAttribute(
      'href',
      '/app/petani',
    );
  });
});
