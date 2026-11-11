import { type FormEvent, useState } from 'react';
import { Badge, Button, Input, Select } from '@/components/atoms';
import {
  FormField,
  PolicyNoticeBanner,
  SearchField,
  StatusIndicator,
} from '@/components/molecules';
import {
  ConfirmDialog,
  DataTable,
  type DataTableColumn,
  FormSection,
  StateFeedbackCard,
} from '@/components/organisms';
import { DataManagementTemplate } from '@/components/templates';
import {
  type AdminUserSummary,
  type SystemRuleVersion,
  useAdminUsers,
  useCreateAdminUser,
  useCreateSystemRuleVersion,
  useSystemRuleVersions,
  useUpdateAdminUser,
} from '@/features/admin/api/adminApi';
import type { components } from '@/lib/api/generated';
import {
  ALL_ROLE_CODES,
  type AuthenticatedUser,
  isNonApproverAdmin,
  ROLE_LABELS,
  type RoleCode,
  type ScopeType,
} from '@/lib/auth/permissions';
import { formatWibDateTime } from '@/lib/decimal/precision';
import { ApiError } from '@/lib/errors/errorCatalog';

type AccountStatus = components['schemas']['AccountStatus'];
type PolicyClassification = components['schemas']['PolicyClassification'];

function formatApiErrorText(err: unknown): string {
  if (err instanceof ApiError) {
    return err.requestId ? `${err.message} (${err.requestId})` : err.message;
  }
  return err instanceof Error ? err.message : 'Terjadi kendala pada permintaan.';
}

export function AdminPenggunaPage({ user }: { readonly user: AuthenticatedUser }) {
  const [search, setSearch] = useState('');
  const [showCreateUser, setShowCreateUser] = useState(false);

  const [newUsername, setNewUsername] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newRole, setNewRole] = useState<RoleCode>('COOPERATIVE_OPERATOR');
  const [newScope, setNewScope] = useState<ScopeType>('PERUMDA_GLOBAL');
  const [newTargetId, setNewTargetId] = useState('');
  const [formError, setFormError] = useState<string | null>(null);
  const [formFeedback, setFormFeedback] = useState<string | null>(null);

  const [editingUser, setEditingUser] = useState<AdminUserSummary | null>(null);
  const [editRole, setEditRole] = useState<RoleCode>('FARMER');
  const [editScope, setEditScope] = useState<ScopeType>('PERUMDA_GLOBAL');
  const [editTargetId, setEditTargetId] = useState('');
  const [editReason, setEditReason] = useState('');

  const [statusTarget, setStatusTarget] = useState<{
    user: AdminUserSummary;
    nextStatus: AccountStatus;
  } | null>(null);

  const [ruleCode, setRuleCode] = useState('RECONCILIATION_WEIGHT_TOLERANCE');
  const [ruleValue, setRuleValue] = useState('1.5000');
  const [ruleClassification, setRuleClassification] =
    useState<PolicyClassification>('SIMULATION_ONLY');
  const [ruleReason, setRuleReason] = useState('');
  const [ruleError, setRuleError] = useState<string | null>(null);
  const [ruleFeedback, setRuleFeedback] = useState<string | null>(null);

  const usersQuery = useAdminUsers(search);
  const rulesQuery = useSystemRuleVersions();
  const createUserMut = useCreateAdminUser();
  const updateUserMut = useUpdateAdminUser();
  const createRuleMut = useCreateSystemRuleVersion();

  const nonApprover = isNonApproverAdmin(user);

  const buildScopeTargets = (scope: ScopeType, targetId: string) => ({
    farmer_id: scope === 'FARMER' ? targetId.trim() || null : null,
    cooperative_id: scope === 'COOPERATIVE' ? targetId.trim() || null : null,
    mill_id: scope === 'MILL' ? targetId.trim() || null : null,
  });

  const handleCreateUser = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormError(null);
    setFormFeedback(null);

    if (newUsername.trim().length < 3) {
      setFormError('Username minimal 3 karakter.');
      return;
    }
    if (newPassword.length < 10) {
      setFormError('Kata sandi awal wajib minimal 10 karakter.');
      return;
    }
    if (newScope !== 'PERUMDA_GLOBAL' && !newTargetId.trim()) {
      setFormError('Scope non-global wajib menyertakan UUID entitas target (Petani/Koperasi/PKS).');
      return;
    }

    try {
      const targets = buildScopeTargets(newScope, newTargetId);
      const res = await createUserMut.mutateAsync({
        username: newUsername.trim(),
        email: newEmail.trim() || null,
        password: newPassword,
        role_code: newRole,
        scope_type: newScope,
        ...targets,
      });
      setFormFeedback(`Akun ${res.data.username} berhasil dibuat dan diaudit.`);
      setNewUsername('');
      setNewEmail('');
      setNewPassword('');
      setNewTargetId('');
      setShowCreateUser(false);
    } catch (err) {
      setFormError(formatApiErrorText(err));
    }
  };

  const handleSaveUserEdit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!editingUser) return;
    setFormError(null);
    setFormFeedback(null);

    if (editReason.trim().length < 5) {
      setFormError('Alasan audit perubahan hak akses wajib minimal 5 karakter.');
      return;
    }
    if (editScope !== 'PERUMDA_GLOBAL' && !editTargetId.trim()) {
      setFormError('Scope non-global wajib menyertakan UUID entitas target.');
      return;
    }

    try {
      const targets = buildScopeTargets(editScope, editTargetId);
      const res = await updateUserMut.mutateAsync({
        userId: editingUser.id,
        payload: {
          role_code: editRole,
          scope_type: editScope,
          ...targets,
          reason: editReason.trim(),
        },
      });
      setFormFeedback(`Hak akses akun ${res.data.username} diperbarui dan dicatat di audit trail.`);
      setEditingUser(null);
      setEditReason('');
    } catch (err) {
      setFormError(formatApiErrorText(err));
    }
  };

  const handleConfirmStatusChange = async (reason: string) => {
    if (!statusTarget) return;
    setFormError(null);
    setFormFeedback(null);
    try {
      const res = await updateUserMut.mutateAsync({
        userId: statusTarget.user.id,
        payload: {
          status: statusTarget.nextStatus,
          reason,
        },
      });
      setFormFeedback(
        `Status akun ${res.data.username} diubah menjadi ${res.data.status}; sesi aktif dicabut jika nonaktif.`,
      );
      setStatusTarget(null);
    } catch (err) {
      setFormError(formatApiErrorText(err));
      setStatusTarget(null);
    }
  };

  const handleCreateRuleVersion = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setRuleError(null);
    setRuleFeedback(null);

    const parsedNum = Number(ruleValue);
    if (!ruleCode.trim() || Number.isNaN(parsedNum) || parsedNum < 0) {
      setRuleError('Masukkan nilai parameter numerik non-negatif yang sah.');
      return;
    }

    const ruleConfig: Record<string, unknown> =
      ruleCode === 'RECONCILIATION_WEIGHT_TOLERANCE'
        ? { tolerance_percent: ruleValue.trim() }
        : ruleCode === 'GRADING_POTONGAN_STANDARD'
          ? { default_potongan_percent: ruleValue.trim() }
          : { decimal_scale: Math.trunc(parsedNum) };

    try {
      const res = await createRuleMut.mutateAsync({
        rule_code: ruleCode,
        effective_from: new Date().toISOString(),
        effective_until: null,
        rule_config: ruleConfig,
        policy_classification: ruleClassification,
        reason: ruleReason.trim() || 'Registrasi versi parameter append-only via portal admin.',
      });
      setRuleFeedback(
        `Versi baru ${res.data.rule_code} v${res.data.version_number} tercatat (${res.data.approval_status} | ${res.data.policy_classification}).`,
      );
      setRuleReason('');
    } catch (err) {
      setRuleError(formatApiErrorText(err));
    }
  };

  const userColumns: DataTableColumn<AdminUserSummary>[] = [
    {
      key: 'username',
      header: 'Akun Pengguna',
      render: (row) => (
        <div>
          <p className="font-mono text-xs font-bold text-ink-primary">{row.username}</p>
          <p className="text-xs text-ink-muted">{row.email ?? 'Tanpa email'}</p>
        </div>
      ),
    },
    {
      key: 'roles',
      header: 'Peran & Cakupan (Scope)',
      render: (row) => {
        const role = row.roles[0] ?? 'FARMER';
        const scope = row.access_scopes[0];
        const target = scope?.farmer_id ?? scope?.cooperative_id ?? scope?.mill_id;
        return (
          <div className="space-y-1 text-xs">
            <p className="font-semibold text-ink-primary">{ROLE_LABELS[role] ?? role}</p>
            <p className="font-mono text-ink-secondary">
              {scope?.scope_type ?? 'PERUMDA_GLOBAL'}
              {target ? ` (${target.slice(0, 8)}...)` : ''}
            </p>
          </div>
        );
      },
    },
    {
      key: 'status',
      header: 'Status & Wewenang',
      render: (row) => (
        <div className="flex flex-wrap items-center gap-1.5">
          <StatusIndicator status={row.status} />
          {row.non_approver_enforced ? (
            <Badge tone="danger">Dilarang Approver</Badge>
          ) : (
            <Badge tone="success">Terisolasi</Badge>
          )}
        </div>
      ),
    },
    {
      key: 'actions',
      header: 'Aksi',
      render: (row) => (
        <div className="flex flex-wrap gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              setEditingUser(row);
              setEditRole(row.roles[0] ?? 'FARMER');
              const sc = row.access_scopes[0];
              setEditScope(sc?.scope_type ?? 'PERUMDA_GLOBAL');
              setEditTargetId(sc?.farmer_id ?? sc?.cooperative_id ?? sc?.mill_id ?? '');
              setEditReason('');
              setFormError(null);
            }}
          >
            Ubah Akses
          </Button>
          {row.status === 'ACTIVE' ? (
            <Button
              size="sm"
              variant="danger"
              disabled={row.id === user.id}
              onClick={() => setStatusTarget({ user: row, nextStatus: 'INACTIVE' })}
            >
              Nonaktifkan
            </Button>
          ) : (
            <Button
              size="sm"
              variant="secondary"
              onClick={() => setStatusTarget({ user: row, nextStatus: 'ACTIVE' })}
            >
              Aktifkan
            </Button>
          )}
        </div>
      ),
    },
  ];

  const ruleRows = rulesQuery.data?.data ?? [];

  return (
    <DataManagementTemplate
      user={user}
      header={{
        eyebrow: 'ADMINISTRASI TI | RBAC & KONFIGURASI',
        title: 'Manajemen Akun, Cakupan RBAC & Aturan Berversi',
        description:
          'Kelola akun internal/mitra, penegakan isolasi cakupan organisasi, pencabutan sesi seketika, serta penambahan aturan berversi append-only (system_rule_versions).',
        actions: (
          <Button
            variant={showCreateUser ? 'outline' : 'primary'}
            onClick={() => {
              setShowCreateUser((v) => !v);
              setFormError(null);
            }}
          >
            {showCreateUser ? 'Tutup Form Akun' : '+ Tambah Akun Pengguna'}
          </Button>
        ),
      }}
      noticeSlot={
        <PolicyNoticeBanner
          kind="non_approver"
          title="Kepatuhan BR-SYS-002 (Non-Approver Administrator)"
          description={
            nonApprover
              ? 'Administrator Sistem mengelola akun dan konfigurasi simulasi/draf, tetapi DILARANG mengesahkan kebijakan produksi, kontrak, atau pencairan keuangan.'
              : 'Perubahan hak akses harus menyertakan alasan audit.'
          }
        />
      }
      filterSlot={
        <div className="max-w-md">
          <SearchField
            value={search}
            onChange={setSearch}
            placeholder="Cari username, email, atau peran..."
            label="Cari Akun"
          />
        </div>
      }
      formSlot={
        <>
          {formFeedback ? (
            <p
              role="status"
              className="rounded-md border border-primary-default/30 bg-primary-subtle px-4 py-2.5 text-sm font-medium text-primary-default"
            >
              {formFeedback}
            </p>
          ) : null}
          {formError ? (
            <p
              role="alert"
              className="rounded-md border border-danger-text/30 bg-danger-bg px-4 py-2.5 text-sm font-medium text-danger-text"
            >
              {formError}
            </p>
          ) : null}

          {showCreateUser ? (
            <form onSubmit={(e) => void handleCreateUser(e)}>
              <FormSection
                title="Buat Akun Pengguna Baru"
                description="Kata sandi di-hash aman di server dan wajib minimal 10 karakter."
                aside={
                  <div className="flex justify-end gap-2">
                    <Button type="button" variant="outline" onClick={() => setShowCreateUser(false)}>
                      Batal
                    </Button>
                    <Button type="submit" isLoading={createUserMut.isPending}>
                      Simpan Akun Baru
                    </Button>
                  </div>
                }
              >
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  <FormField id="new-username" label="Username" required>
                    <Input
                      id="new-username"
                      value={newUsername}
                      onChange={(e) => setNewUsername(e.target.value)}
                      placeholder="contoh: opr_kop_02"
                      required
                    />
                  </FormField>
                  <FormField id="new-email" label="Email (Opsional)">
                    <Input
                      id="new-email"
                      type="email"
                      value={newEmail}
                      onChange={(e) => setNewEmail(e.target.value)}
                      placeholder="nama@domain.id"
                    />
                  </FormField>
                  <FormField id="new-password" label="Kata Sandi Awal (min 10)" required>
                    <Input
                      id="new-password"
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      required
                    />
                  </FormField>
                  <FormField id="new-role" label="Peran" required>
                    <Select
                      id="new-role"
                      value={newRole}
                      onChange={(e) => setNewRole(e.target.value as RoleCode)}
                    >
                      {ALL_ROLE_CODES.map((code) => (
                        <option key={code} value={code}>
                          {ROLE_LABELS[code]} ({code})
                        </option>
                      ))}
                    </Select>
                  </FormField>
                  <FormField id="new-scope" label="Cakupan Data (Scope)" required>
                    <Select
                      id="new-scope"
                      value={newScope}
                      onChange={(e) => setNewScope(e.target.value as ScopeType)}
                    >
                      <option value="PERUMDA_GLOBAL">PERUMDA_GLOBAL</option>
                      <option value="COOPERATIVE">COOPERATIVE</option>
                      <option value="MILL">MILL</option>
                      <option value="FARMER">FARMER</option>
                    </Select>
                  </FormField>
                  {newScope !== 'PERUMDA_GLOBAL' ? (
                    <FormField
                      id="new-target-id"
                      label={`UUID Target ${newScope}`}
                      required
                      helperText="Wajib diisi saat cakupan bukan PERUMDA_GLOBAL"
                    >
                      <Input
                        id="new-target-id"
                        value={newTargetId}
                        onChange={(e) => setNewTargetId(e.target.value)}
                        placeholder="00000000-0000-4000-8000-..."
                        required
                      />
                    </FormField>
                  ) : null}
                </div>
              </FormSection>
            </form>
          ) : null}

          {editingUser ? (
            <form onSubmit={(e) => void handleSaveUserEdit(e)}>
              <FormSection
                title={`Ubah Hak Akses: ${editingUser.username}`}
                description="Setiap perubahan peran atau scope dicatat di audit trail."
                aside={
                  <div className="flex justify-end gap-2">
                    <Button type="button" variant="outline" onClick={() => setEditingUser(null)}>
                      Batal
                    </Button>
                    <Button type="submit" isLoading={updateUserMut.isPending}>
                      Simpan Perubahan Akses
                    </Button>
                  </div>
                }
              >
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  <FormField id="edit-role" label="Peran" required>
                    <Select
                      id="edit-role"
                      value={editRole}
                      onChange={(e) => setEditRole(e.target.value as RoleCode)}
                    >
                      {ALL_ROLE_CODES.map((code) => (
                        <option key={code} value={code}>
                          {ROLE_LABELS[code]} ({code})
                        </option>
                      ))}
                    </Select>
                  </FormField>
                  <FormField id="edit-scope" label="Scope" required>
                    <Select
                      id="edit-scope"
                      value={editScope}
                      onChange={(e) => setEditScope(e.target.value as ScopeType)}
                    >
                      <option value="PERUMDA_GLOBAL">PERUMDA_GLOBAL</option>
                      <option value="COOPERATIVE">COOPERATIVE</option>
                      <option value="MILL">MILL</option>
                      <option value="FARMER">FARMER</option>
                    </Select>
                  </FormField>
                  {editScope !== 'PERUMDA_GLOBAL' ? (
                    <FormField id="edit-target" label={`UUID Target ${editScope}`} required>
                      <Input
                        id="edit-target"
                        value={editTargetId}
                        onChange={(e) => setEditTargetId(e.target.value)}
                        required
                      />
                    </FormField>
                  ) : null}
                  <FormField id="edit-reason" label="Alasan Audit (min 5)" required>
                    <Input
                      id="edit-reason"
                      value={editReason}
                      onChange={(e) => setEditReason(e.target.value)}
                      placeholder="Mutasi tugas operasional"
                      required
                    />
                  </FormField>
                </div>
              </FormSection>
            </form>
          ) : null}
        </>
      }
    >
      <div className="grid gap-6 xl:grid-cols-3">
        <div className="xl:col-span-2">
          {usersQuery.isError ? (
            <StateFeedbackCard
              variant="error"
              title="Gagal Memuat Daftar Akun"
              error={usersQuery.error}
              onAction={() => void usersQuery.refetch()}
            />
          ) : (
            <DataTable
              caption="Daftar Akun Pengguna dan Cakupan RBAC"
              columns={userColumns}
              rows={usersQuery.data?.data ?? []}
              getRowKey={(r) => r.id}
              isLoading={usersQuery.isLoading}
              emptyTitle="Akun Tidak Ditemukan"
              emptyDescription="Tidak ada akun yang cocok dengan kata kunci pencarian."
            />
          )}
        </div>

        <div className="space-y-4">
          <div className="rounded-xl border border-border-subtle bg-surface-default p-5 shadow-sm">
            <h2 className="text-base font-bold text-ink-primary">
              Parameter Aturan Berversi (Append-Only)
            </h2>
            <p className="mt-1 text-xs text-ink-secondary">
              Registrasi versi baru tidak mengubah histori rekonsiliasi atau grading transaksi
              lampau.
            </p>

            {ruleFeedback ? (
              <p
                role="status"
                className="mt-3 rounded bg-primary-subtle px-3 py-2 text-xs font-medium text-primary-default"
              >
                {ruleFeedback}
              </p>
            ) : null}
            {ruleError ? (
              <p
                role="alert"
                className="mt-3 rounded bg-danger-bg px-3 py-2 text-xs font-medium text-danger-text"
              >
                {ruleError}
              </p>
            ) : null}

            <form onSubmit={(e) => void handleCreateRuleVersion(e)} className="mt-4 space-y-3">
              <FormField id="rule-code" label="Kode Aturan" required>
                <Select
                  id="rule-code"
                  value={ruleCode}
                  onChange={(e) => setRuleCode(e.target.value)}
                >
                  <option value="RECONCILIATION_WEIGHT_TOLERANCE">
                    RECONCILIATION_WEIGHT_TOLERANCE
                  </option>
                  <option value="GRADING_POTONGAN_STANDARD">GRADING_POTONGAN_STANDARD</option>
                  <option value="ROUNDING_DECIMAL_SCALE">ROUNDING_DECIMAL_SCALE</option>
                </Select>
              </FormField>
              <FormField
                id="rule-value"
                label={
                  ruleCode === 'ROUNDING_DECIMAL_SCALE'
                    ? 'Jumlah Desimal'
                    : 'Nilai Persentase (%)'
                }
                required
              >
                <Input
                  id="rule-value"
                  value={ruleValue}
                  onChange={(e) => setRuleValue(e.target.value)}
                  required
                />
              </FormField>
              <FormField
                id="rule-policy"
                label="Klasifikasi Kebijakan"
                required
                helperText={
                  nonApprover
                    ? 'SYSTEM_ADMIN diblokir untuk CONFIRMED (BR-SYS-002).'
                    : undefined
                }
              >
                <Select
                  id="rule-policy"
                  value={ruleClassification}
                  onChange={(e) => setRuleClassification(e.target.value as PolicyClassification)}
                >
                  <option value="SIMULATION_ONLY">SIMULATION_ONLY</option>
                  <option value="PENDING_SOP">PENDING_SOP</option>
                  <option value="CONFIRMED">CONFIRMED</option>
                </Select>
              </FormField>
              <FormField id="rule-reason" label="Catatan Versi">
                <Input
                  id="rule-reason"
                  value={ruleReason}
                  onChange={(e) => setRuleReason(e.target.value)}
                  placeholder="Usulan toleransi simulasi baru"
                />
              </FormField>
              <Button type="submit" className="w-full" isLoading={createRuleMut.isPending}>
                Buat Versi Aturan Baru
              </Button>
            </form>

            <div className="mt-5 space-y-2 border-t border-border-subtle pt-4">
              <p className="text-xs font-bold uppercase tracking-wide text-ink-muted">
                Riwayat Versi Aturan ({ruleRows.length})
              </p>
              {ruleRows.slice(0, 6).map((rule: SystemRuleVersion) => (
                <div
                  key={rule.id}
                  className="rounded-md border border-border-subtle bg-surface-subtle p-2.5 text-xs"
                >
                  <div className="flex flex-wrap items-center justify-between gap-1">
                    <span className="font-mono font-bold text-ink-primary">
                      {rule.rule_code} v{rule.version_number}
                    </span>
                    <StatusIndicator status={rule.approval_status} />
                  </div>
                  <p className="mt-1 text-ink-secondary">
                    Klasifikasi: {rule.policy_classification} | Berlaku{' '}
                    {formatWibDateTime(rule.effective_from)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <ConfirmDialog
        open={Boolean(statusTarget)}
        title={
          statusTarget?.nextStatus === 'INACTIVE'
            ? `Nonaktifkan & Cabut Sesi ${statusTarget.user.username}`
            : `Aktifkan Kembali ${statusTarget?.user.username ?? ''}`
        }
        description="Perubahan status akun dicatat permanen dalam log audit keamanan dan sesi aktif akan langsung dicabut jika dinonaktifkan."
        confirmLabel={statusTarget?.nextStatus === 'INACTIVE' ? 'Nonaktifkan Akun' : 'Aktifkan'}
        tone={statusTarget?.nextStatus === 'INACTIVE' ? 'danger' : 'primary'}
        requireReason
        reasonPlaceholder="Minimal 5 karakter (contoh: Resign atau mutasi cabang)..."
        isSubmitting={updateUserMut.isPending}
        onConfirm={(reason) => void handleConfirmStatusChange(reason)}
        onCancel={() => setStatusTarget(null)}
      />
    </DataManagementTemplate>
  );
}
