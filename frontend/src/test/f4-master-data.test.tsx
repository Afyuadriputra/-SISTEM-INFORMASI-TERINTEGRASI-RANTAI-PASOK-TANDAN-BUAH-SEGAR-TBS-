import { QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider, createMemoryHistory } from '@tanstack/react-router';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
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

describe('F4 Master Data UI (FLOW-05 & FLOW-06)', () => {
  it('completes FLOW-05 create farmer, paired coordinate validation, and audited deactivation', async () => {
    const user = userEvent.setup();
    await loginWithCredentials({
      username: 'sim_kop_op_01',
      password: MOCK_SIMULATION_PASSWORD,
    });

    renderRoute('/app/koperasi');

    expect(
      await screen.findByRole('heading', { name: /Dashboard & Master Data Koperasi/i }, { timeout: 4000 }),
    ).toBeInTheDocument();

    // Verify existing scoped farmer appears cleanly
    expect(await screen.findByText('Hendra Wijaya')).toBeInTheDocument();

    // Register a new farmer (FLOW-05A)
    await user.type(screen.getByLabelText(/Kode Petani/i), 'PTN-SIM-NEW-01');
    await user.selectOptions(
      screen.getByLabelText(/Koperasi Pengelola/i),
      '40000000-0000-4000-8000-000000000001',
    );
    await user.type(screen.getByLabelText(/Nama Lengkap Petani/i), 'Siti Rahma Baru');
    await user.type(screen.getByLabelText(/Nomor Kontak/i), '081234567890');
    await user.click(screen.getByRole('button', { name: /Simpan Data Petani/i }));

    expect(await screen.findByText('Siti Rahma Baru')).toBeInTheDocument();

    // Test paired coordinates validation in FLOW-05B (latitude filled, longitude empty -> inline error)
    const farmerSelect = screen.getByLabelText(/Petani Pemilik Kebun/i);
    const firstFarmerOpt = screen.getByRole('option', { name: /PET-PLW-001/i }) as HTMLOptionElement;
    await user.selectOptions(farmerSelect, firstFarmerOpt.value);
    await user.type(screen.getByLabelText(/Kode Kebun/i), 'KBN-SIM-NEW-01');
    await user.type(screen.getByLabelText(/Nama \/ Lokasi Kebun/i), 'Kebun Sejahtera');
    await user.type(screen.getByLabelText(/Luas \(ha\)/i), '2.2500');
    await user.type(screen.getByLabelText(/Desa \/ Kelurahan/i), 'Makmur');
    await user.type(screen.getByLabelText(/^Kecamatan/i), 'Pangkalan Kerinci');
    await user.type(screen.getByLabelText(/^Latitude/i), '0.401200');
    await user.click(screen.getByRole('button', { name: /Simpan Data Kebun/i }));

    expect(await screen.findByRole('alert')).toHaveTextContent(/wajib diisi berpasangan/i);

    // Auditable status deactivation (never hard delete)
    const deactivateButtons = screen.getAllByRole('button', { name: /Nonaktifkan/i });
    await user.click(deactivateButtons[0]);
    expect(await screen.findByRole('dialog')).toBeInTheDocument();
    await user.type(screen.getByLabelText(/Alasan Tindakan/i), 'Petani pindah domisili sesuai surat.');
    await user.click(screen.getByRole('button', { name: /Simpan Perubahan Status/i }));

    await waitFor(() => {
      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });
    expect(screen.getAllByText('Nonaktif').length).toBeGreaterThan(0);
  });

  it('completes FLOW-06 create Mill PKS with explicit publication confirmation', async () => {
    const user = userEvent.setup();
    await loginWithCredentials({
      username: 'sim_perumda_ops_01',
      password: MOCK_SIMULATION_PASSWORD,
    });

    renderRoute('/app/perumda');
    expect(
      await screen.findByRole('heading', { name: /Dashboard Operasional & Master Data PKS/i }, { timeout: 4000 }),
    ).toBeInTheDocument();

    await user.selectOptions(
      await screen.findByLabelText(/Perusahaan Induk/i),
      '30000000-0000-4000-8000-000000000101',
    );
    await user.type(screen.getByLabelText(/Kode PKS/i), 'PKS-TES-09');
    await user.type(screen.getByLabelText(/Nama Unit PKS/i), 'PKS Tuah Harapan');
    await user.type(screen.getByLabelText(/Alamat Lengkap PKS/i), 'Jl. Lintas Bono KM 12');
    await user.type(screen.getByLabelText(/^Kecamatan/i), 'Pangkalan Kerinci');
    await user.type(screen.getByLabelText(/^Latitude/i), '0.382100');
    await user.type(screen.getByLabelText(/^Longitude/i), '101.901200');
    await user.click(screen.getByLabelText(/Setujui Publikasi Profil PKS/i));
    await user.click(screen.getByRole('button', { name: /Simpan Data PKS/i }));

    // Confirmation modal must intercept public publication
    expect(await screen.findByRole('dialog')).toHaveTextContent(/Publikasi Profil PKS/i);
    await user.click(screen.getByRole('button', { name: /Ya, Publikasikan Profil PKS/i }));

    expect(await screen.findByText('PKS Tuah Harapan')).toBeInTheDocument();
  });
});
