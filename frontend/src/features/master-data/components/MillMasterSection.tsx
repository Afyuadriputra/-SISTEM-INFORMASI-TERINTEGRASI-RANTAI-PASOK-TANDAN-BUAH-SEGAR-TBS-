import { zodResolver } from '@hookform/resolvers/zod';
import { Edit3, Globe, Plus } from 'lucide-react';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Badge, Button, Checkbox, Input, Select } from '@/components/atoms';
import {
  FormField,
  LocationLink,
  PolicyNoticeBanner,
  StatusIndicator,
} from '@/components/molecules';
import { ConfirmDialog, DataTable, FormSection, StateFeedbackCard } from '@/components/organisms';
import { ApiError } from '@/lib/errors/errorCatalog';
import { useUiStore } from '@/lib/state/uiStore';
import {
  useCreateMill,
  useMillCompanies,
  useMills,
  useUpdateMill,
  type Mill,
} from '../api/masterDataApi';

const millSchema = z
  .object({
    mill_company_id: z.string().min(1, 'Pilih perusahaan induk PKS.'),
    mill_code: z.string().trim().min(3, 'Kode PKS minimal 3 karakter.').max(40),
    mill_name: z.string().trim().min(3, 'Nama PKS minimal 3 karakter.').max(140),
    address: z.string().trim().min(5, 'Alamat lengkap PKS wajib diisi.'),
    district: z.string().trim().min(2, 'Kecamatan wajib diisi.'),
    regency: z.string().trim().min(2, 'Kabupaten wajib diisi.'),
    province: z.string().trim().min(2, 'Provinsi wajib diisi.'),
    contact_phone: z.string().trim().optional(),
    partnership_status: z.enum(['ACTIVE', 'INACTIVE']),
    is_public: z.boolean(),
    latitude: z.string().trim().optional(),
    longitude: z.string().trim().optional(),
  })
  .refine(
    (data) => {
      const lat = data.latitude?.trim() ?? '';
      const lon = data.longitude?.trim() ?? '';
      if (Boolean(lat) !== Boolean(lon)) return false;
      if (!lat) return true;
      const la = Number(lat);
      const lo = Number(lon);
      return Number.isFinite(la) && Number.isFinite(lo) && la >= -90 && la <= 90 && lo >= -180 && lo <= 180;
    },
    {
      message:
        'Latitude (-90 s.d. 90) dan Longitude (-180 s.d. 180) wajib berpasangan atau dikosongkan keduanya.',
      path: ['longitude'],
    },
  );

type MillFormValues = z.infer<typeof millSchema>;

export function MillMasterSection({ canWrite }: { readonly canWrite: boolean }) {
  const pushToast = useUiStore((s) => s.pushToast);
  const companiesQuery = useMillCompanies();
  const millsQuery = useMills();
  const createMill = useCreateMill();
  const updateMill = useUpdateMill();

  const [editingMill, setEditingMill] = useState<Mill | null>(null);
  const [pendingPublicSave, setPendingPublicSave] = useState<MillFormValues | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const companies = companiesQuery.data?.data ?? [];
  const mills = millsQuery.data?.data ?? [];

  const form = useForm<MillFormValues>({
    resolver: zodResolver(millSchema),
    defaultValues: {
      mill_company_id: '',
      mill_code: '',
      mill_name: '',
      address: '',
      district: '',
      regency: 'Pelalawan',
      province: 'Riau',
      contact_phone: '',
      partnership_status: 'ACTIVE',
      is_public: false,
      latitude: '',
      longitude: '',
    },
  });

  const resetToCreate = () => {
    setEditingMill(null);
    setFormError(null);
    form.reset({
      mill_company_id: companies[0]?.id ?? '',
      mill_code: '',
      mill_name: '',
      address: '',
      district: '',
      regency: 'Pelalawan',
      province: 'Riau',
      contact_phone: '',
      partnership_status: 'ACTIVE',
      is_public: false,
      latitude: '',
      longitude: '',
    });
  };

  const startEditMill = (mill: Mill) => {
    setEditingMill(mill);
    setFormError(null);
    form.reset({
      mill_company_id: mill.mill_company_id,
      mill_code: mill.mill_code,
      mill_name: mill.mill_name,
      address: mill.address,
      district: mill.district ?? '',
      regency: mill.regency,
      province: mill.province,
      contact_phone: mill.contact_phone ?? '',
      partnership_status: mill.partnership_status,
      is_public: mill.is_public,
      latitude: mill.latitude ?? '',
      longitude: mill.longitude ?? '',
    });
  };

  const executeSave = async (values: MillFormValues) => {
    setFormError(null);
    try {
      if (editingMill) {
        await updateMill.mutateAsync({
          millId: editingMill.id,
          payload: {
            mill_name: values.mill_name,
            address: values.address,
            district: values.district,
            regency: values.regency,
            latitude: values.latitude?.trim() || null,
            longitude: values.longitude?.trim() || null,
            contact_phone: values.contact_phone?.trim() || null,
            partnership_status: values.partnership_status,
            is_public: values.is_public,
            version: editingMill.version,
          },
        });
        pushToast({
          tone: 'success',
          title: `Master PKS ${editingMill.mill_code} diperbarui (Publik: ${values.is_public ? 'Ya' : 'Tidak'}).`,
        });
        resetToCreate();
      } else {
        const res = await createMill.mutateAsync({
          mill_company_id: values.mill_company_id,
          mill_code: values.mill_code,
          mill_name: values.mill_name,
          address: values.address,
          district: values.district,
          regency: values.regency,
          province: values.province,
          latitude: values.latitude?.trim() || null,
          longitude: values.longitude?.trim() || null,
          contact_phone: values.contact_phone?.trim() || null,
          partnership_status: values.partnership_status,
          is_public: values.is_public,
        });
        pushToast({
          tone: 'success',
          title: `PKS ${res.data.mill_code} berhasil ditambahkan.`,
          requestId: res.request_id,
        });
        resetToCreate();
      }
    } catch (error) {
      if (error instanceof ApiError) {
        setFormError(`${error.code}: ${error.message}`);
      } else {
        setFormError('Gagal menyimpan data PKS.');
      }
    }
  };

  const onSubmit = (values: MillFormValues) => {
    // Require explicit confirmation before publishing a PKS profile publicly (FLOW-06 / BR-PUB-004).
    const changingToPublic = values.is_public && (!editingMill || !editingMill.is_public);
    if (changingToPublic) {
      setPendingPublicSave(values);
      return;
    }
    void executeSave(values);
  };

  return (
    <div className="space-y-6">
      <PolicyNoticeBanner
        kind="info"
        title="Kontrol Publikasi Profil PKS (FLOW-06 & BR-PUB-004)"
        description="Status kemitraan internal ACTIVE tidak otomatis menayangkan PKS di Portal Publik. Hanya PKS dengan status publikasi disetujui (is_public = true) serta koordinat terverifikasi yang dipublikasikan."
      />

      {formError ? (
        <div
          role="alert"
          className="rounded-md border border-danger-text/30 bg-danger-bg px-4 py-3 text-sm font-medium text-danger-text"
        >
          {formError}
        </div>
      ) : null}

      {canWrite ? (
        <FormSection
          stepNumber="FLOW-06"
          title={editingMill ? `Ubah Master PKS: ${editingMill.mill_code}` : 'Tambah Master Data PKS Mitra'}
          description="Lengkapi identitas pabrik, koordinat berpasangan, kontak yang disetujui, serta pengaturan publikasi."
          aside={
            editingMill ? (
              <Button size="sm" variant="outline" onClick={resetToCreate}>
                Batal Ubah
              </Button>
            ) : null
          }
        >
          <form onSubmit={(e) => void form.handleSubmit(onSubmit)(e)} noValidate className="space-y-4">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <FormField
                id="mill-company"
                label="Perusahaan Induk"
                required
                error={form.formState.errors.mill_company_id?.message}
              >
                <Select
                  id="mill-company"
                  disabled={Boolean(editingMill)}
                  hasError={Boolean(form.formState.errors.mill_company_id)}
                  {...form.register('mill_company_id')}
                >
                  <option value="">-- Pilih Perusahaan PKS --</option>
                  {companies.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.company_code} - {c.company_name}
                    </option>
                  ))}
                </Select>
              </FormField>

              <FormField
                id="mill-code"
                label="Kode PKS"
                required
                error={form.formState.errors.mill_code?.message}
              >
                <Input
                  id="mill-code"
                  monospace
                  disabled={Boolean(editingMill)}
                  placeholder="PKS-PLW-04"
                  hasError={Boolean(form.formState.errors.mill_code)}
                  {...form.register('mill_code')}
                />
              </FormField>

              <FormField
                id="mill-name"
                label="Nama Unit PKS"
                required
                error={form.formState.errors.mill_name?.message}
              >
                <Input
                  id="mill-name"
                  placeholder="PKS Tuah Jaya"
                  hasError={Boolean(form.formState.errors.mill_name)}
                  {...form.register('mill_name')}
                />
              </FormField>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div className="sm:col-span-2">
                <FormField
                  id="mill-address"
                  label="Alamat Lengkap PKS"
                  required
                  error={form.formState.errors.address?.message}
                >
                  <Input
                    id="mill-address"
                    placeholder="Jl. Lintas Timur KM ..."
                    hasError={Boolean(form.formState.errors.address)}
                    {...form.register('address')}
                  />
                </FormField>
              </div>
              <FormField id="mill-phone" label="Kontak Publik Resmi PKS">
                <Input id="mill-phone" placeholder="0761-..." {...form.register('contact_phone')} />
              </FormField>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
              <FormField
                id="mill-district"
                label="Kecamatan"
                required
                error={form.formState.errors.district?.message}
              >
                <Input
                  id="mill-district"
                  placeholder="Pangkalan Kerinci"
                  hasError={Boolean(form.formState.errors.district)}
                  {...form.register('district')}
                />
              </FormField>
              <FormField
                id="mill-regency"
                label="Kabupaten"
                required
                error={form.formState.errors.regency?.message}
              >
                <Input
                  id="mill-regency"
                  hasError={Boolean(form.formState.errors.regency)}
                  {...form.register('regency')}
                />
              </FormField>
              <FormField id="mill-lat" label="Latitude">
                <Input id="mill-lat" monospace placeholder="0.412345" {...form.register('latitude')} />
              </FormField>
              <FormField
                id="mill-lon"
                label="Longitude"
                error={form.formState.errors.longitude?.message}
              >
                <Input
                  id="mill-lon"
                  monospace
                  placeholder="101.856789"
                  hasError={Boolean(form.formState.errors.longitude)}
                  {...form.register('longitude')}
                />
              </FormField>
            </div>

            <div className="flex flex-col gap-3 rounded-md border border-border-subtle bg-surface-subtle/50 p-4 sm:flex-row sm:items-center sm:justify-between">
              <div className="space-y-1">
                <label htmlFor="mill-status" className="block text-xs font-semibold text-ink-secondary">
                  Status Kemitraan Internal
                </label>
                <Select id="mill-status" {...form.register('partnership_status')}>
                  <option value="ACTIVE">ACTIVE (Aktif Bermitra)</option>
                  <option value="INACTIVE">INACTIVE (Nonaktif)</option>
                </Select>
              </div>

              <Checkbox
                id="mill-is-public"
                label="Setujui Publikasi Profil PKS ke Portal Publik (is_public)"
                {...form.register('is_public')}
              />
            </div>

            <Button
              type="submit"
              isLoading={createMill.isPending || updateMill.isPending}
              leadingIcon={<Plus aria-hidden="true" className="h-4 w-4" />}
            >
              {editingMill ? 'Simpan Pembaruan PKS' : 'Simpan Data PKS'}
            </Button>
          </form>
        </FormSection>
      ) : null}

      {millsQuery.isError ? (
        <StateFeedbackCard
          variant="error"
          error={millsQuery.error}
          onAction={() => void millsQuery.refetch()}
        />
      ) : (
        <DataTable<Mill>
          caption="Master Data PKS Mitra Perumda"
          rows={mills}
          isLoading={millsQuery.isLoading}
          getRowKey={(row) => row.id}
          columns={[
            {
              key: 'identity',
              header: 'PKS Mitra',
              render: (row) => (
                <div>
                  <p className="font-mono text-xs font-bold text-primary-default">{row.mill_code}</p>
                  <p className="font-semibold text-ink-primary">{row.mill_name}</p>
                  <p className="text-xs text-text-muted">{row.company_name}</p>
                </div>
              ),
            },
            {
              key: 'location',
              header: 'Lokasi & Koordinat',
              render: (row) => (
                <LocationLink
                  address={row.address}
                  district={row.district}
                  regency={row.regency}
                  latitude={row.latitude}
                  longitude={row.longitude}
                  hasVerifiedCoordinates={row.has_verified_coordinates}
                />
              ),
            },
            {
              key: 'visibility',
              header: 'Status & Publikasi',
              render: (row) => (
                <div className="space-y-1.5">
                  <StatusIndicator status={row.partnership_status} />
                  <div>
                    <Badge tone={row.is_public ? 'primary' : 'neutral'}>
                      <Globe aria-hidden="true" className="h-3 w-3" />
                      <span>{row.is_public ? 'Terpublikasi Publik' : 'Privat Internal'}</span>
                    </Badge>
                  </div>
                </div>
              ),
            },
            {
              key: 'actions',
              header: 'Aksi',
              render: (row) =>
                canWrite ? (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => startEditMill(row)}
                    leadingIcon={<Edit3 aria-hidden="true" className="h-3.5 w-3.5" />}
                  >
                    Kelola PKS
                  </Button>
                ) : (
                  <span className="text-xs text-text-muted">Hanya baca</span>
                ),
            },
          ]}
        />
      )}

      <ConfirmDialog
        open={Boolean(pendingPublicSave)}
        title="Konfirmasi Publikasi Profil PKS ke Portal Publik"
        description="Setelah disetujui sebagai publik, nama pabrik, alamat, kontak resmi PKS, serta koordinat terverifikasi dapat dilihat tanpa login di Portal Publik. Kontrak komersial tetap tersembunyi."
        confirmLabel="Ya, Publikasikan Profil PKS"
        isSubmitting={createMill.isPending || updateMill.isPending}
        onConfirm={async () => {
          if (pendingPublicSave) {
            const payload = pendingPublicSave;
            setPendingPublicSave(null);
            await executeSave(payload);
          }
        }}
        onCancel={() => setPendingPublicSave(null)}
      />
    </div>
  );
}
