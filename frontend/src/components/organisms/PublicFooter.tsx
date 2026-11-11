import { Link } from '@tanstack/react-router';

export function PublicFooter() {
  return (
    <footer className="mt-16 border-t border-border-subtle bg-surface-default">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          <div className="space-y-2">
            <p className="text-sm font-bold text-ink-primary">
              Perumda Tuah Sekata (Unit Agro Niaga)
            </p>
            <p className="text-xs leading-relaxed text-ink-secondary">
              Sistem Informasi Terintegrasi Rantai Pasok Tandan Buah Segar (TBS) Kabupaten
              Pelalawan.
            </p>
            <p className="text-xs text-text-muted">
              Cakupan layanan portal ini khusus untuk rantai pasok TBS kelapa sawit (Unit Listrik
              & Gas tidak termasuk dalam sistem).
            </p>
          </div>
          <div className="space-y-2">
            <p className="text-xs font-bold uppercase tracking-wide text-ink-secondary">
              Portal Publik
            </p>
            <ul className="space-y-1.5 text-sm">
              <li>
                <Link to="/harga-tbs" className="text-ink-secondary hover:text-primary-default">
                  Perbandingan Harga Multi-PKS
                </Link>
              </li>
              <li>
                <Link to="/lokasi-pks" className="text-ink-secondary hover:text-primary-default">
                  Lokasi Kantor & PKS Mitra
                </Link>
              </li>
              <li>
                <Link to="/tentang" className="text-ink-secondary hover:text-primary-default">
                  Profil Perumda & Tata Kelola
                </Link>
              </li>
              <li>
                <Link to="/kemitraan" className="text-ink-secondary hover:text-primary-default">
                  Informasi Kemitraan
                </Link>
              </li>
            </ul>
          </div>
          <div className="space-y-2">
            <p className="text-xs font-bold uppercase tracking-wide text-ink-secondary">
              Keamanan & Akses
            </p>
            <p className="text-xs leading-relaxed text-ink-secondary">
              Portal Publik tidak menampilkan data pribadi petani, kontrak komersial rahasia, atau
              rekening transaksi internal (BR-PUB-001..005).
            </p>
            <p className="pt-1">
              <Link
                to="/kontak"
                className="text-sm font-semibold text-primary-default underline hover:text-brand-hover"
              >
                Hubungi Kontak Resmi
              </Link>
            </p>
          </div>
        </div>
        <div className="mt-8 border-t border-border-subtle pt-4 text-xs text-text-muted">
          Perumda Tuah Sekata Unit Agro Niaga | Seluruh tampilan waktu pada aplikasi menggunakan
          zona Waktu Indonesia Barat (WIB, UTC+7).
        </div>
      </div>
    </footer>
  );
}
