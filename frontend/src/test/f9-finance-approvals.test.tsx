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

describe('F9 Finance, Invoice, Payment, Executive Approval & Farmer Transparency', () => {
  it('blocks DISPUTE_HOLD invoice drafting (FIN_DISPUTE_HOLD_BLOCKED), blocks UNCONFIRMED issue (FIN_POLICY_UNCONFIRMED), and blocks partial payment (PAY_PARTIAL_NOT_SUPPORTED)', async () => {
    const user = userEvent.setup();
    await loginWithCredentials({
      username: 'sim_perumda_fin_01',
      password: MOCK_SIMULATION_PASSWORD,
    });

    renderRoute('/app/perumda/pembayaran');
    expect(
      await screen.findByRole(
        'heading',
        { name: /Manajemen Faktur & Pencatatan Pembayaran Manual Terverifikasi/i },
        { timeout: 5000 },
      ),
    ).toBeInTheDocument();

    // Verify FIN_DISPUTE_HOLD_BLOCKED when attempting invoice draft from DISPUTE_HOLD case
    const disputeOpt = (await screen.findByRole('option', {
      name: /DISPUTE_HOLD/,
    })) as HTMLOptionElement;
    await user.selectOptions(screen.getByLabelText(/Kasus Rekonsiliasi/i), disputeOpt.value);
    await user.click(screen.getByRole('button', { name: /Buat Draf Faktur/i }));
    expect(await screen.findByRole('alert')).toHaveTextContent(/FIN_DISPUTE_HOLD_BLOCKED/);

    // Verify FIN_POLICY_UNCONFIRMED on PENDING_SOP draft invoice issuance
    const issueButtons = screen.getAllByRole('button', { name: /Terbitkan Faktur/i });
    await user.click(issueButtons[0]);
    expect(await screen.findByRole('alert')).toHaveTextContent(/FIN_POLICY_UNCONFIRMED/);

    // Verify PAY_PARTIAL_NOT_SUPPORTED on partial amount against INV-AP-2026-1110-001 (AWAITING_PAYMENT)
    const invPaySelect = screen.getByLabelText(/Faktur Terbit/i);
    const apOpt = screen.getByRole('option', {
      name: /INV-AP-2026-1110-001/,
    }) as HTMLOptionElement;
    await user.selectOptions(invPaySelect, apOpt.value);
    await user.type(screen.getByLabelText(/Nominal Bayar/i), '1000.00');
    await user.type(screen.getByLabelText(/Nomor Referensi/i), 'REF-PARTIAL-01');
    await user.click(screen.getByRole('button', { name: /Catat Bukti Pembayaran/i }));
    expect(await screen.findByRole('alert')).toHaveTextContent(/PAY_PARTIAL_NOT_SUPPORTED/);
  });

  it('renders /app/direksi/persetujuan and read-only /app/petani & /app/petani/panen cleanly', async () => {
    const user = userEvent.setup();
    await logoutSession().catch(() => undefined);
    await loginWithCredentials({
      username: 'sim_director_01',
      password: MOCK_SIMULATION_PASSWORD,
    });

    renderRoute('/app/direksi/persetujuan');
    expect(
      await screen.findByRole(
        'heading',
        { name: /Pusat Persetujuan Pembayaran, Sengketa & Kontrak/i },
        { timeout: 5000 },
      ),
    ).toBeInTheDocument();

    // Resolve dispute as Director
    const resolveButtons = await screen.findAllByRole('button', {
      name: /Putuskan Sengketa/i,
    });
    await user.click(resolveButtons[0]);
    expect(await screen.findByRole('dialog')).toBeInTheDocument();
    await user.type(
      screen.getByLabelText(/Alasan Tindakan/i),
      'Disepakati memakai berita acara timbangan PKS resmi.',
    );
    await user.click(screen.getByRole('button', { name: /Sahkan Keputusan/i }));

    // Farmer read-only portal
    await logoutSession();
    await loginWithCredentials({
      username: 'sim_petani_01',
      password: MOCK_SIMULATION_PASSWORD,
    });

    renderRoute('/app/petani/panen');
    expect(
      await screen.findByRole(
        'heading',
        { name: /Riwayat Penimbangan Panen & Pembayaran Anda/i },
        { timeout: 5000 },
      ),
    ).toBeInTheDocument();
    expect(await screen.findByText(/RCV-2026-1110-001/)).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /Simpan Penimbangan/i })).not.toBeInTheDocument();
  });
});
