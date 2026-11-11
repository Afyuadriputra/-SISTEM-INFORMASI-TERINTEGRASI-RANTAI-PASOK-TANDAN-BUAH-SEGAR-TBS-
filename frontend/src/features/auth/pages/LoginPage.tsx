import { zodResolver } from '@hookform/resolvers/zod';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useSearch } from '@tanstack/react-router';
import { Eye, EyeOff, Lock, ShieldCheck } from 'lucide-react';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Button, Input } from '@/components/atoms';
import { FormField, PolicyNoticeBanner } from '@/components/molecules';
import { AuthTemplate } from '@/components/templates';
import {
  canAccessRoutePath,
  getRoleHomePath,
  ROLE_LABELS,
  type RoleCode,
} from '@/lib/auth/permissions';
import { fetchCurrentUser, loginWithCredentials, logoutSession } from '@/lib/auth/session';
import { isMockApiMode } from '@/lib/config/env';
import { ApiError } from '@/lib/errors/errorCatalog';
import { queryKeys } from '@/lib/query/queryKeys';

const loginSchema = z.object({
  username: z.string().trim().min(3, 'Username minimal 3 karakter.').max(100),
  password: z.string().min(8, 'Kata sandi minimal 8 karakter.').max(128),
});

type LoginFormValues = z.infer<typeof loginSchema>;

const MOCK_QUICK_ACTORS: ReadonlyArray<{ username: string; role: RoleCode }> = [
  { username: 'sim_petani_01', role: 'FARMER' },
  { username: 'sim_kop_op_01', role: 'COOPERATIVE_OPERATOR' },
  { username: 'sim_perumda_ops_01', role: 'PERUMDA_OPERATIONS' },
  { username: 'sim_perumda_fin_01', role: 'PERUMDA_FINANCE' },
  { username: 'sim_mill_op_01', role: 'MILL_OPERATOR' },
  { username: 'sim_director_01', role: 'DIRECTOR' },
  { username: 'sim_sys_admin_01', role: 'SYSTEM_ADMIN' },
];

function isSafeInternalTarget(rawNext: unknown): rawNext is string {
  return (
    typeof rawNext === 'string' &&
    rawNext.startsWith('/app/') &&
    !rawNext.startsWith('//') &&
    !rawNext.includes('://')
  );
}

export function LoginPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const search = useSearch({ strict: false }) as { next?: unknown };
  const [showPassword, setShowPassword] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [requestId, setRequestId] = useState<string | null>(null);

  const sessionQuery = useQuery({
    queryKey: queryKeys.auth.me(),
    queryFn: fetchCurrentUser,
    staleTime: 10_000,
  });

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { username: '', password: '' },
  });

  const onSubmit = async (values: LoginFormValues) => {
    setSubmitError(null);
    setRequestId(null);
    try {
      const user = await loginWithCredentials(values);
      queryClient.setQueryData(queryKeys.auth.me(), user);
      const nextPath =
        isSafeInternalTarget(search.next) && canAccessRoutePath(user, search.next)
          ? search.next
          : getRoleHomePath(user);
      await navigate({ to: nextPath, replace: true });
    } catch (error) {
      if (error instanceof ApiError) {
        setSubmitError(error.message);
        setRequestId(error.requestId);
      } else {
        setSubmitError('Gagal menghubungi layanan autentikasi. Coba beberapa saat lagi.');
      }
    }
  };

  const handleLogoutCurrent = async () => {
    await logoutSession();
    await queryClient.invalidateQueries({ queryKey: queryKeys.auth.me() });
  };

  const activeUser = sessionQuery.data ?? null;
  const mockMode = isMockApiMode();

  return (
    <AuthTemplate>
      <div className="grid grid-cols-1 gap-8 lg:grid-cols-12 lg:items-start">
        <section className="space-y-4 lg:col-span-5">
          <p className="font-mono text-xs font-semibold uppercase tracking-wide text-primary-default">
            AKSES PORTAL INTERNAL
          </p>
          <h1 className="text-2xl font-bold tracking-tight text-ink-primary sm:text-3xl">
            Masuk Sistem Rantai Pasok TBS
          </h1>
          <p className="text-sm leading-relaxed text-ink-secondary">
            Gunakan kredensial akun resmi Perumda Tuah Sekata, koperasi mitra, petugas PKS, atau
            petani terdaftar. Sesi dijaga dengan cookie aman HttpOnly dan proteksi CSRF.
          </p>
          <div className="rounded-lg border border-border-subtle bg-surface-default p-4 text-xs leading-relaxed text-ink-secondary">
            <div className="flex items-start gap-2.5">
              <ShieldCheck aria-hidden="true" className="mt-0.5 h-4 w-4 shrink-0 text-primary-default" />
              <div>
                <p className="font-semibold text-ink-primary">Pembatasan Hak Akses & Audit</p>
                <p className="mt-0.5">
                  Setiap halaman dan data hanya dapat dibuka sesuai peran dan cakupan organisasi
                  akun Anda (BR-026). Seluruh percobaan masuk tercatat pada log keamanan.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="space-y-5 rounded-lg border border-border-subtle bg-surface-default p-6 shadow-xs lg:col-span-7">
          {activeUser ? (
            <div className="space-y-4 rounded-md border border-primary-default/25 bg-primary-subtle/50 p-4">
              <p className="text-sm font-bold text-ink-primary">
                Sesi Aktif: {activeUser.display_name} ({activeUser.username})
              </p>
              <p className="text-xs text-ink-secondary">
                Peran: {activeUser.roles.map((r) => ROLE_LABELS[r] ?? r).join(', ')}
              </p>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant="primary"
                  onClick={() => void navigate({ to: getRoleHomePath(activeUser) })}
                >
                  Masuk ke Beranda Peran
                </Button>
                <Button variant="outline" onClick={() => void handleLogoutCurrent()}>
                  Keluar & Ganti Akun
                </Button>
              </div>
            </div>
          ) : null}

          {submitError ? (
            <div
              role="alert"
              className="rounded-md border border-danger-text/30 bg-danger-bg px-4 py-3 text-sm text-danger-text"
            >
              <p className="font-semibold">{submitError}</p>
              {requestId ? (
                <p className="mt-1 font-mono text-xs opacity-90">Ref: {requestId}</p>
              ) : null}
            </div>
          ) : null}

          <form onSubmit={(e) => void handleSubmit(onSubmit)(e)} noValidate className="space-y-4">
            <FormField
              id="login-username"
              label="Username"
              required
              error={errors.username?.message}
            >
              <Input
                id="login-username"
                type="text"
                autoComplete="username"
                hasError={Boolean(errors.username)}
                placeholder="Masukkan username akun Anda"
                {...register('username')}
              />
            </FormField>

            <FormField
              id="login-password"
              label="Kata Sandi"
              required
              error={errors.password?.message}
            >
              <div className="relative">
                <Input
                  id="login-password"
                  type={showPassword ? 'text' : 'password'}
                  autoComplete="current-password"
                  hasError={Boolean(errors.password)}
                  placeholder="Minimal 8 karakter"
                  className="pr-12"
                  {...register('password')}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((prev) => !prev)}
                  aria-label={showPassword ? 'Sembunyikan kata sandi' : 'Tampilkan kata sandi'}
                  className="absolute top-1/2 right-1 flex h-10 w-10 -translate-y-1/2 items-center justify-center rounded text-ink-secondary hover:text-ink-primary"
                >
                  {showPassword ? (
                    <EyeOff aria-hidden="true" className="h-4 w-4" />
                  ) : (
                    <Eye aria-hidden="true" className="h-4 w-4" />
                  )}
                </button>
              </div>
            </FormField>

            <Button
              type="submit"
              variant="primary"
              fullWidth
              isLoading={isSubmitting}
              leadingIcon={<Lock aria-hidden="true" className="h-4 w-4" />}
            >
              Masuk ke Portal Internal
            </Button>
          </form>

          {mockMode ? (
            <div className="space-y-3 border-t border-border-subtle pt-4">
              <PolicyNoticeBanner
                kind="simulation"
                title="Mode Simulasi MSW Aktif (Non-Produksi)"
                description="Pilih aktor simulasi di bawah untuk mengisi kredensial demo lokal pada pengujian MSW. Fitur ini otomatis nonaktif pada mode LIVE FASTAPI."
              />
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                {MOCK_QUICK_ACTORS.map((actor) => (
                  <button
                    key={actor.username}
                    type="button"
                    onClick={() => {
                      setValue('username', actor.username, { shouldValidate: true });
                      setValue('password', 'Simulasi123!', { shouldValidate: true });
                    }}
                    className="flex min-h-[44px] flex-col items-start justify-center rounded-md border border-border-subtle bg-surface-subtle/60 px-3 py-1.5 text-left hover:border-primary-default hover:bg-primary-subtle/50"
                  >
                    <span className="font-mono text-xs font-bold text-ink-primary">
                      {actor.username}
                    </span>
                    <span className="text-[11px] text-ink-secondary">{ROLE_LABELS[actor.role]}</span>
                  </button>
                ))}
              </div>
            </div>
          ) : null}
        </section>
      </div>
    </AuthTemplate>
  );
}
