import { QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider, createMemoryHistory } from '@tanstack/react-router';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { INTERNAL_PAGE_MAP, PUBLIC_AND_AUTH_PAGE_MAP } from '@/app/router/routePageRegistry';
import { createAppRouter } from '@/app/router/router';
import { CANONICAL_ROUTES } from '@/lib/auth/permissions';
import { appQueryClient } from '@/lib/query/queryClient';
import { mockDb } from '@/mocks/mockDb';

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

function loginAs(username: string) {
  const actor = mockDb.users.find((u) => u.username === username);
  if (!actor) throw new Error(`Missing mock actor ${username}`);
  mockDb.currentUserId = actor.id;
}

describe('F10 Dashboards, Analytics & Admin Portal', () => {
  it('registers all 26 AFD §36 canonical routes without stubs remaining', () => {
    expect(CANONICAL_ROUTES).toHaveLength(26);
    for (const route of CANONICAL_ROUTES) {
      if (route.access === 'internal') {
        expect(INTERNAL_PAGE_MAP[route.path]).toBeDefined();
      } else {
        expect(PUBLIC_AND_AUTH_PAGE_MAP[route.path]).toBeDefined();
      }
    }
  });

  it('renders DIRECTOR executive dashboard with separated cash/AR/AP metrics and non-net-profit margin label (BR-MRG-005)', async () => {
    loginAs('sim_director_01');
    renderRoute('/app/direksi');

    expect(
      await screen.findByRole(
        'heading',
        { name: /Dashboard Eksekutif Direksi/i },
        { timeout: 5000 },
      ),
    ).toBeInTheDocument();

    expect(
      await screen.findByText(/Kontribusi Kotor Niaga \(Data Simulasi - Bukan Laba Bersih\)/i),
    ).toBeInTheDocument();
    expect(screen.getAllByText(/Bukan Laba Bersih/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Piutang PKS \(AR\) vs Kas Masuk Riil/i)).toBeInTheDocument();
    expect(screen.getByText(/Hutang Disetujui vs Terbayar/i)).toBeInTheDocument();
    expect(screen.getByText(/Realisasi Tonase Kebun vs PKS/i)).toBeInTheDocument();
  });

  it('enforces SYSTEM_ADMIN non-approver CCTV dashboard and append-only rules / user deactivation audit', async () => {
    const user = userEvent.setup();
    loginAs('sim_sys_admin_01');
    renderRoute('/app/admin');

    expect(
      await screen.findByRole(
        'heading',
        { name: /Dashboard Administrasi Teknis & Kesehatan Sistem/i },
        { timeout: 5000 },
      ),
    ).toBeInTheDocument();

    expect(screen.getAllByText(/Non-Approver \(BR-SYS-002\)/i).length).toBeGreaterThan(0);
    expect(await screen.findByText(/SEHAT \(UP\)/i)).toBeInTheDocument();
    expect(await screen.findByText(/req-sim-8f2a1c90/i)).toBeInTheDocument();
    expect(screen.queryByText(/Rp /i)).not.toBeInTheDocument();

    renderRoute('/app/admin/pengguna');
    expect(
      await screen.findByRole(
        'heading',
        { name: /Manajemen Akun, Cakupan RBAC & Aturan Berversi/i },
        { timeout: 5000 },
      ),
    ).toBeInTheDocument();

    // SYSTEM_ADMIN cannot set CONFIRMED -> server blocks BR-SYS-002
    const beforeRulesCount = mockDb.systemRuleVersions.length;
    await user.selectOptions(screen.getByLabelText(/Klasifikasi Kebijakan/i), 'CONFIRMED');
    await user.click(screen.getByRole('button', { name: /Buat Versi Aturan Baru/i }));
    expect(await screen.findByText(/SYSTEM_ADMIN dilarang mengesahkan kebijakan/i)).toBeInTheDocument();
    expect(mockDb.systemRuleVersions).toHaveLength(beforeRulesCount);

    // Append-only SIMULATION_ONLY rule creation succeeds cleanly
    await user.selectOptions(screen.getByLabelText(/Klasifikasi Kebijakan/i), 'SIMULATION_ONLY');
    await user.clear(screen.getByLabelText(/Nilai Persentase/i));
    await user.type(screen.getByLabelText(/Nilai Persentase/i), '1.7500');
    await user.click(screen.getByRole('button', { name: /Buat Versi Aturan Baru/i }));
    expect(
      await screen.findByText(/RECONCILIATION_WEIGHT_TOLERANCE v\d+ tercatat/i),
    ).toBeInTheDocument();
    expect(mockDb.systemRuleVersions).toHaveLength(beforeRulesCount + 1);

    // Deactivate a non-self user with mandatory reason
    const deactivateButtons = await screen.findAllByRole('button', { name: /^Nonaktifkan$/i });
    const enabledDeactivate = deactivateButtons.find((btn) => !(btn as HTMLButtonElement).disabled);
    expect(enabledDeactivate).toBeDefined();
    await user.click(enabledDeactivate!);
    await user.type(
      await screen.findByPlaceholderText(/Minimal 5 karakter/i),
      'Mutasi operator lapangan ke cabang baru',
    );
    await user.click(screen.getByRole('button', { name: /Nonaktifkan Akun/i }));

    await waitFor(() => {
      expect(mockDb.auditEvents[0]?.action).toBe('ADMIN_USER_REVOKED');
    });

    // DIRECTOR can also read append-only audit trail
    loginAs('sim_director_01');
    renderRoute('/app/admin/audit');
    expect(
      await screen.findByRole(
        'heading',
        { name: /Audit Trail Append-Only & CCTV Digital/i },
        { timeout: 5000 },
      ),
    ).toBeInTheDocument();
    expect(await screen.findByText(/ADMIN_USER_REVOKED/i)).toBeInTheDocument();
    expect(screen.getByText(/RULE_VERSION_CREATED/i)).toBeInTheDocument();
  });
});
