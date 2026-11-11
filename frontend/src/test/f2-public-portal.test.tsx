import { QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider, createMemoryHistory } from '@tanstack/react-router';
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { createAppRouter } from '@/app/router/router';
import { appQueryClient } from '@/lib/query/queryClient';

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

describe('F2 Public Portal (7 Anonymous Routes)', () => {
  it('renders Beranda / with Disbun price separated from verified PKS quotes', async () => {
    renderRoute('/');

    expect(
      await screen.findByRole(
        'heading',
        {
          name: /Transparansi Harga TBS Multi-PKS/i,
        },
        { timeout: 5000 },
      ),
    ).toBeInTheDocument();

    expect(await screen.findByText(/Pembanding Resmi \(BR-004\)/i)).toBeInTheDocument();
    expect((await screen.findAllByText(/PKS Pangkalan Kerinci/i)).length).toBeGreaterThan(0);
    expect(screen.queryByText(/PKS Ukui Barat/i)).not.toBeInTheDocument();
  });

  it('filters and toggles expired quotes on /harga-tbs without mixing Disbun into PKS ranking', async () => {
    const user = userEvent.setup();
    renderRoute('/harga-tbs');

    expect(
      await screen.findByRole(
        'heading',
        { name: /Perbandingan Harga TBS Multi-PKS/i },
        { timeout: 5000 },
      ),
    ).toBeInTheDocument();
    expect(await screen.findByText(/Referensi Resmi Dinas Perkebunan/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getAllByText(/PKS-PKC-01/).length).toBeGreaterThan(0);
    });
    expect(screen.queryByText('Kedaluwarsa')).not.toBeInTheDocument();

    const expiredCheckbox = screen.getByLabelText(/Sertakan harga kedaluwarsa/i);
    await user.click(expiredCheckbox);
    expect(await screen.findByText('Kedaluwarsa')).toBeInTheDocument();
  });

  it('renders /pks/:id detail and blocks unpublished PKS (is_public=false) cleanly with 404', async () => {
    renderRoute('/pks/30000000-0000-4000-8000-000000000001');
    expect(await screen.findByRole('heading', { name: /PKS Pangkalan Kerinci/i })).toBeInTheDocument();
    expect(screen.getAllByText(/BR-PUB-004/).length).toBeGreaterThan(0);

    renderRoute('/pks/30000000-0000-4000-8000-000000000003');
    expect(await screen.findByRole('alert')).toHaveTextContent(/SYS_RESOURCE_NOT_FOUND/);
  });

  it('renders /lokasi-pks, /tentang, /kemitraan, and /kontak cleanly without farmer PII', async () => {
    renderRoute('/lokasi-pks');
    expect(
      await screen.findByRole('heading', { name: /Lokasi Kantor Perumda & PKS Mitra/i }),
    ).toBeInTheDocument();
    expect(await screen.findByText(/PKS Pangkalan Kerinci/i)).toBeInTheDocument();
    expect(await screen.findByText(/tanpa pin perkiraan/i)).toBeInTheDocument();

    renderRoute('/tentang');
    expect(await screen.findByText(/Listrik & Gas/i)).toBeInTheDocument();

    renderRoute('/kemitraan');
    expect(await screen.findByText(/FR-PUB-007/)).toBeInTheDocument();

    renderRoute('/kontak');
    expect(
      await screen.findByRole('heading', { name: /Kontak Resmi Unit Agro Niaga/i }),
    ).toBeInTheDocument();
  });
});
