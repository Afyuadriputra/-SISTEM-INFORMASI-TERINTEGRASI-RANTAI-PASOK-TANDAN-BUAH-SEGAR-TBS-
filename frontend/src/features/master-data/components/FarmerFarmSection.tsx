import { zodResolver } from '@hookform/resolvers/zod';
import { Edit3, Plus, UserX } from 'lucide-react';
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Button, Input, Select } from '@/components/atoms';
import {
  FormField,
  LocationLink,
  SearchField,
  StatusIndicator,
} from '@/components/molecules';
import {
  ConfirmDialog,
  DataTable,
  FormSection,
  StateFeedbackCard,
} from '@/components/organisms';
import type { AuthenticatedUser } from '@/lib/auth/permissions';
import { formatHectares } from '@/lib/decimal/precision';
import { ApiError } from '@/lib/errors/errorCatalog';
import { useUiStore } from '@/lib/state/uiStore';
import {
  useCooperatives,
  useCreateFarm,
  useCreateFarmer,
  useFarmers,
  useFarms,
  useUpdateFarm,
  useUpdateFarmer,
  type Farm,
  type Farmer,
} from '../api/masterDataApi';

const farmerSchema = z.object({
  farmer_code: z.string().trim().min(3, 'Kode petani minimal 3 karakter.').max(40),
  full_name: z.string().trim().min(3, 'Nama lengkap minimal 3 karakter.').max(120),
  contact_phone: z.string().trim().min(8, 'Nomor kontak minimal 8 karakter.').max(30),
  cooperative_id: z.string().min(1, 'Pilih koperasi pengelola.'),
  membership_number: z.string().trim().max(60).optional(),
});

type FarmerFormValues = z.infer<typeof farmerSchema>;

const coordRefine = (data: { latitude?: string; longitude?: string }) => {
  const lat = data.latitude?.trim() ?? '';
  const lon = data.longitude?.trim() ?? '';
  if (Boolean(lat) !== Boolean(lon)) {
    return false;
  }
  if (!lat) {
    return true;
  }
  const latNum = Number(lat);
  const lonNum = Number(lon);
  return (
    Number.isFinite(latNum) &&
    Number.isFinite(lonNum) &&
    latNum >= -90 &&
    latNum <= 90 &&
    lonNum >= -180 &&
    lonNum <= 180
  );
};

const farmSchema = z
  .object({
    farmer_id: z.string().min(1, 'Pilih petani pemilik kebun.'),
    farm_code: z.string().trim().min(3, 'Kode kebun minimal 3 karakter.').max(40),
    farm_name: z.string().trim().min(3, 'Nama kebun minimal 3 karakter.').max(120),
    area_hectares: z
      .string()
      .trim()
      .refine((v) => /^\d+(\.\d{1,4})?$/.test(v) && Number(v) > 0, {
        message: 'Luas lahan wajib berupa angka positif (maks. 4 desimal ha).',
      }),
    planting_year: z.string().trim().optional(),
    stdb_number: z.string().trim().max(60).optional(),
    village: z.string().trim().min(2, 'Nama desa wajib diisi (minimal 2 karakter).').max(100),
    district: z.string().trim().min(2, 'Nama kecamatan wajib diisi (minimal 2 karakter).').max(100),
    latitude: z.string().trim().optional(),
    longitude: z.string().trim().optional(),
  })
  .refine(coordRefine, {
    message:
      'Koordinat wajib diisi berpasangan (Latitude -90 s.d. 90, Longitude -180 s.d. 180) atau dikosongkan keduanya.',
    path: ['longitude'],
  });

type FarmFormValues = z.infer<typeof farmSchema>;

export function FarmerFarmSection({
  user,
  canWrite,
}: {
  readonly user: AuthenticatedUser;
  readonly canWrite: boolean;
}) {
  const pushToast = useUiStore((s) => s.pushToast);
  const defaultCoopId =
    user.access_scopes.find((s) => s.scope_type === 'COOPERATIVE')?.cooperative_id ?? '';

  const [search, setSearch] = useState('');
  const [editingFarmer, setEditingFarmer] = useState<Farmer | null>(null);
  const [editingFarm, setEditingFarm] = useState<Farm | null>(null);
  const [farmerToToggleStatus, setFarmerToToggleStatus] = useState<Farmer | null>(null);
  const [formError, setFormError] = useState<string | null>(null);

  const coopsQuery = useCooperatives();
  const farmersQuery = useFarmers(search);
  const farmsQuery = useFarms();

  const createFarmer = useCreateFarmer();
  const updateFarmer = useUpdateFarmer();
  const createFarm = useCreateFarm();
  const updateFarm = useUpdateFarm();

  const coops = coopsQuery.data?.data ?? [];
  const farmers = farmersQuery.data?.data ?? [];
  const farms = farmsQuery.data?.data ?? [];

  const farmerForm = useForm<FarmerFormValues>({
    resolver: zodResolver(farmerSchema),
    defaultValues: {
      farmer_code: '',
      full_name: '',
      contact_phone: '',
      cooperative_id: defaultCoopId,
      membership_number: '',
    },
  });

  const farmForm = useForm<FarmFormValues>({
    resolver: zodResolver(farmSchema),
    defaultValues: {
      farmer_id: '',
      farm_code: '',
      farm_name: '',
      area_hectares: '',
      planting_year: '2018',
      stdb_number: '',
      village: '',
      district: '',
      latitude: '',
      longitude: '',
    },
  });

  const startCreateFarmer = () => {
    setEditingFarmer(null);
    setFormError(null);
    farmerForm.reset({
      farmer_code: '',
      full_name: '',
      contact_phone: '',
      cooperative_id: defaultCoopId || coops[0]?.id || '',
      membership_number: '',
    });
  };

  const startEditFarmer = (farmer: Farmer) => {
    setEditingFarmer(farmer);
    setFormError(null);
    farmerForm.reset({
      farmer_code: farmer.farmer_code,
      full_name: farmer.full_name,
      contact_phone: farmer.contact_phone ?? '',
      cooperative_id: farmer.cooperative_id,
      membership_number: farmer.membership_number ?? '',
    });
  };

  const startCreateFarm = () => {
    setEditingFarm(null);
    setFormError(null);
    farmForm.reset({
      farmer_id: farmers[0]?.id ?? '',
      farm_code: '',
      farm_name: '',
      area_hectares: '',
      planting_year: '2018',
      stdb_number: '',
      village: '',
      district: '',
      latitude: '',
      longitude: '',
    });
  };

  const startEditFarm = (farm: Farm) => {
    setEditingFarm(farm);
    setFormError(null);
    farmForm.reset({
      farmer_id: farm.farmer_id,
      farm_code: farm.farm_code,
      farm_name: farm.farm_name,
      area_hectares: farm.area_hectares,
      planting_year: farm.planting_year ? String(farm.planting_year) : '',
      stdb_number: farm.stdb_number ?? '',
      village: farm.village ?? '',
      district: farm.district ?? '',
      latitude: farm.latitude ?? '',
      longitude: farm.longitude ?? '',
    });
  };

  const handleFarmerSubmit = async (values: FarmerFormValues) => {
    setFormError(null);
    try {
      if (editingFarmer) {
        await updateFarmer.mutateAsync({
          farmerId: editingFarmer.id,
          payload: {
            full_name: values.full_name,
            contact_phone: values.contact_phone?.trim() ? values.contact_phone.trim() : null,
            status: editingFarmer.status,
            reason: 'Pembaruan profil petani melalui FLOW-05',
            version: editingFarmer.version,
          },
        });
        pushToast({
          tone: 'success',
          title: `Profil petani ${editingFarmer.farmer_code} diperbarui.`,
        });
        setEditingFarmer(null);
      } else {
        const res = await createFarmer.mutateAsync({
          farmer_code: values.farmer_code,
          full_name: values.full_name,
          contact_phone: values.contact_phone,
          cooperative_id: values.cooperative_id,
          membership_number: values.membership_number?.trim()
            ? values.membership_number.trim()
            : null,
        });
        pushToast({
          tone: 'success',
          title: `Petani ${res.data.farmer_code} berhasil didaftarkan.`,
          requestId: res.request_id,
        });
        startCreateFarmer();
      }
    } catch (error) {
      if (error instanceof ApiError) {
        setFormError(`${error.code}: ${error.message}`);
      } else {
        setFormError('Gagal menyimpan data petani.');
      }
    }
  };

  const handleFarmSubmit = async (values: FarmFormValues) => {
    setFormError(null);
    const parsedYear = values.planting_year ? Number(values.planting_year) : null;
    const normalizedArea = Number(values.area_hectares).toFixed(4);
    try {
      if (editingFarm) {
        await updateFarm.mutateAsync({
          farmId: editingFarm.id,
          payload: {
            farm_name: values.farm_name,
            area_hectares: normalizedArea,
            planting_year: Number.isFinite(parsedYear) ? parsedYear : null,
            stdb_number: values.stdb_number?.trim() || null,
            village: values.village,
            district: values.district,
            latitude: values.latitude?.trim() || null,
            longitude: values.longitude?.trim() || null,
            version: editingFarm.version,
          },
        });
        pushToast({
          tone: 'success',
          title: `Data kebun ${editingFarm.farm_code} diperbarui.`,
        });
        setEditingFarm(null);
      } else {
        const res = await createFarm.mutateAsync({
          farmer_id: values.farmer_id,
          farm_code: values.farm_code,
          farm_name: values.farm_name,
          area_hectares: normalizedArea,
          planting_year: Number.isFinite(parsedYear) ? parsedYear : null,
          stdb_number: values.stdb_number?.trim() || null,
          village: values.village,
          district: values.district,
          latitude: values.latitude?.trim() || null,
          longitude: values.longitude?.trim() || null,
        });
        pushToast({
          tone: 'success',
          title: `Kebun ${res.data.farm_code} berhasil ditambahkan.`,
          requestId: res.request_id,
        });
        startCreateFarm();
      }
    } catch (error) {
      if (error instanceof ApiError) {
        setFormError(`${error.code}: ${error.message}`);
      } else {
        setFormError('Gagal menyimpan data kebun.');
      }
    }
  };

  const handleConfirmToggleFarmerStatus = async (reason: string) => {
    if (!farmerToToggleStatus) return;
    const nextStatus = farmerToToggleStatus.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE';
    try {
      await updateFarmer.mutateAsync({
        farmerId: farmerToToggleStatus.id,
        payload: {
          status: nextStatus,
          reason,
          version: farmerToToggleStatus.version,
        },
      });
      pushToast({
        tone: 'info',
        title: `Status petani ${farmerToToggleStatus.farmer_code} diubah menjadi ${nextStatus}.`,
      });
      setFarmerToToggleStatus(null);
    } catch (error) {
      if (error instanceof ApiError) {
        setFormError(`${error.code}: ${error.message}`);
      }
      setFarmerToToggleStatus(null);
    }
  };

  return (
    <div className="space-y-6">
      {formError ? (
        <div
          role="alert"
          className="rounded-md border border-danger-text/30 bg-danger-bg px-4 py-3 text-sm font-medium text-danger-text"
        >
          {formError}
        </div>
      ) : null}

      {canWrite ? (
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
          <FormSection
            stepNumber="FLOW-05A"
            title={editingFarmer ? `Ubah Petani: ${editingFarmer.farmer_code}` : 'Daftarkan Petani Baru'}
            description="Setiap petani wajib terikat pada koperasi dalam cakupan akses operator dan kode unik."
            aside={
              editingFarmer ? (
                <Button size="sm" variant="outline" onClick={startCreateFarmer}>
                  Batal Ubah
                </Button>
              ) : null
            }
          >
            <form
              onSubmit={(e) => void farmerForm.handleSubmit(handleFarmerSubmit)(e)}
              noValidate
              className="space-y-3"
            >
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <FormField
                  id="farmer-code"
                  label="Kode Petani"
                  required
                  error={farmerForm.formState.errors.farmer_code?.message}
                >
                  <Input
                    id="farmer-code"
                    monospace
                    disabled={Boolean(editingFarmer)}
                    placeholder="PTN-KOP01-09"
                    hasError={Boolean(farmerForm.formState.errors.farmer_code)}
                    {...farmerForm.register('farmer_code')}
                  />
                </FormField>

                <FormField
                  id="farmer-coop"
                  label="Koperasi Pengelola"
                  required
                  error={farmerForm.formState.errors.cooperative_id?.message}
                >
                  <Select
                    id="farmer-coop"
                    disabled={Boolean(editingFarmer)}
                    hasError={Boolean(farmerForm.formState.errors.cooperative_id)}
                    {...farmerForm.register('cooperative_id')}
                  >
                    <option value="">-- Pilih Koperasi --</option>
                    {coops.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.cooperative_code} - {c.cooperative_name}
                      </option>
                    ))}
                  </Select>
                </FormField>
              </div>

              <FormField
                id="farmer-name"
                label="Nama Lengkap Petani"
                required
                error={farmerForm.formState.errors.full_name?.message}
              >
                <Input
                  id="farmer-name"
                  placeholder="Nama sesuai identitas"
                  hasError={Boolean(farmerForm.formState.errors.full_name)}
                  {...farmerForm.register('full_name')}
                />
              </FormField>

              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <FormField id="farmer-phone" label="Nomor Kontak">
                  <Input id="farmer-phone" placeholder="0812..." {...farmerForm.register('contact_phone')} />
                </FormField>
                <FormField id="farmer-member" label="Nomor Anggota Koperasi">
                  <Input
                    id="farmer-member"
                    monospace
                    placeholder="ANG-2026-01"
                    {...farmerForm.register('membership_number')}
                  />
                </FormField>
              </div>

              <Button
                type="submit"
                isLoading={createFarmer.isPending || updateFarmer.isPending}
                leadingIcon={<Plus aria-hidden="true" className="h-4 w-4" />}
              >
                {editingFarmer ? 'Simpan Perubahan Petani' : 'Simpan Data Petani'}
              </Button>
            </form>
          </FormSection>

          <FormSection
            stepNumber="FLOW-05B"
            title={editingFarm ? `Ubah Kebun: ${editingFarm.farm_code}` : 'Tambah / Kelola Data Kebun'}
            description="Luas lahan memakai presisi hingga 4 desimal (ha) dan koordinat harus diisi berpasangan."
            aside={
              editingFarm ? (
                <Button size="sm" variant="outline" onClick={startCreateFarm}>
                  Batal Ubah
                </Button>
              ) : null
            }
          >
            <form
              onSubmit={(e) => void farmForm.handleSubmit(handleFarmSubmit)(e)}
              noValidate
              className="space-y-3"
            >
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <FormField
                  id="farm-farmer"
                  label="Petani Pemilik Kebun"
                  required
                  error={farmForm.formState.errors.farmer_id?.message}
                >
                  <Select
                    id="farm-farmer"
                    disabled={Boolean(editingFarm)}
                    hasError={Boolean(farmForm.formState.errors.farmer_id)}
                    {...farmForm.register('farmer_id')}
                  >
                    <option value="">-- Pilih Petani --</option>
                    {farmers.map((fm) => (
                      <option key={fm.id} value={fm.id}>
                        {fm.farmer_code} - {fm.full_name}
                      </option>
                    ))}
                  </Select>
                </FormField>

                <FormField
                  id="farm-code"
                  label="Kode Kebun"
                  required
                  error={farmForm.formState.errors.farm_code?.message}
                >
                  <Input
                    id="farm-code"
                    monospace
                    disabled={Boolean(editingFarm)}
                    placeholder="KBN-PKC-09"
                    hasError={Boolean(farmForm.formState.errors.farm_code)}
                    {...farmForm.register('farm_code')}
                  />
                </FormField>
              </div>

              <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                <div className="sm:col-span-2">
                  <FormField
                    id="farm-name"
                    label="Nama / Lokasi Kebun"
                    required
                    error={farmForm.formState.errors.farm_name?.message}
                  >
                    <Input
                      id="farm-name"
                      placeholder="Kebun Blok B Makmur"
                      hasError={Boolean(farmForm.formState.errors.farm_name)}
                      {...farmForm.register('farm_name')}
                    />
                  </FormField>
                </div>
                <FormField
                  id="farm-area"
                  label="Luas (ha)"
                  required
                  error={farmForm.formState.errors.area_hectares?.message}
                >
                  <Input
                    id="farm-area"
                    monospace
                    placeholder="2.5000"
                    hasError={Boolean(farmForm.formState.errors.area_hectares)}
                    {...farmForm.register('area_hectares')}
                  />
                </FormField>
              </div>

              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <FormField id="farm-year" label="Tahun Tanam">
                  <Input id="farm-year" monospace placeholder="2018" {...farmForm.register('planting_year')} />
                </FormField>
                <FormField id="farm-stdb" label="Nomor STDB (Opsional)">
                  <Input id="farm-stdb" monospace placeholder="STDB-PLW-..." {...farmForm.register('stdb_number')} />
                </FormField>
              </div>

              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <FormField
                  id="farm-village"
                  label="Desa / Kelurahan"
                  required
                  error={farmForm.formState.errors.village?.message}
                >
                  <Input
                    id="farm-village"
                    placeholder="Makmur"
                    hasError={Boolean(farmForm.formState.errors.village)}
                    {...farmForm.register('village')}
                  />
                </FormField>
                <FormField
                  id="farm-district"
                  label="Kecamatan"
                  required
                  error={farmForm.formState.errors.district?.message}
                >
                  <Input
                    id="farm-district"
                    placeholder="Pangkalan Kerinci"
                    hasError={Boolean(farmForm.formState.errors.district)}
                    {...farmForm.register('district')}
                  />
                </FormField>
              </div>

              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                <FormField id="farm-lat" label="Latitude (-90 s.d. 90)">
                  <Input id="farm-lat" monospace placeholder="0.391200" {...farmForm.register('latitude')} />
                </FormField>
                <FormField
                  id="farm-lon"
                  label="Longitude (-180 s.d. 180)"
                  error={farmForm.formState.errors.longitude?.message}
                >
                  <Input
                    id="farm-lon"
                    monospace
                    placeholder="101.854100"
                    hasError={Boolean(farmForm.formState.errors.longitude)}
                    {...farmForm.register('longitude')}
                  />
                </FormField>
              </div>

              <Button
                type="submit"
                isLoading={createFarm.isPending || updateFarm.isPending}
                leadingIcon={<Plus aria-hidden="true" className="h-4 w-4" />}
              >
                {editingFarm ? 'Simpan Perubahan Kebun' : 'Simpan Data Kebun'}
              </Button>
            </form>
          </FormSection>
        </div>
      ) : null}

      <section className="space-y-3">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="text-lg font-bold text-ink-primary">Daftar Petani Terdaftar</h2>
          <div className="w-full sm:max-w-xs">
            <SearchField
              id="search-farmer"
              value={search}
              onChange={setSearch}
              placeholder="Cari nama atau kode petani..."
            />
          </div>
        </div>

        {farmersQuery.isError ? (
          <StateFeedbackCard
            variant="error"
            error={farmersQuery.error}
            onAction={() => void farmersQuery.refetch()}
          />
        ) : (
          <DataTable<Farmer>
            caption="Master Data Petani Swadaya"
            rows={farmers}
            isLoading={farmersQuery.isLoading}
            getRowKey={(row) => row.id}
            columns={[
              {
                key: 'code',
                header: 'Kode & Nama',
                render: (row) => (
                  <div>
                    <p className="font-mono text-xs font-bold text-primary-default">
                      {row.farmer_code}
                    </p>
                    <p className="font-semibold text-ink-primary">{row.full_name}</p>
                    <p className="text-xs text-text-muted">Anggota: {row.membership_number || '-'}</p>
                  </div>
                ),
              },
              {
                key: 'contact',
                header: 'Kontak',
                render: (row) => <span className="text-xs">{row.contact_phone || '-'}</span>,
              },
              {
                key: 'status',
                header: 'Status',
                render: (row) => (
                  <div className="space-y-1">
                    <StatusIndicator status={row.status} />
                    <p className="font-mono text-[11px] text-text-muted">v{row.version}</p>
                  </div>
                ),
              },
              {
                key: 'actions',
                header: 'Aksi',
                render: (row) =>
                  canWrite ? (
                    <div className="flex flex-wrap gap-2">
                      <Button size="sm" variant="outline" onClick={() => startEditFarmer(row)} leadingIcon={<Edit3 aria-hidden="true" className="h-3.5 w-3.5" />}>
                        Ubah
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setFarmerToToggleStatus(row)}
                        leadingIcon={<UserX aria-hidden="true" className="h-3.5 w-3.5" />}
                      >
                        {row.status === 'ACTIVE' ? 'Nonaktifkan' : 'Aktifkan'}
                      </Button>
                    </div>
                  ) : (
                    <span className="text-xs text-text-muted">Hanya baca</span>
                  ),
              },
            ]}
          />
        )}
      </section>

      <section className="space-y-3">
        <h2 className="text-lg font-bold text-ink-primary">Daftar Kebun & Profil Lahan</h2>
        {farmsQuery.isError ? (
          <StateFeedbackCard
            variant="error"
            error={farmsQuery.error}
            onAction={() => void farmsQuery.refetch()}
          />
        ) : (
          <DataTable<Farm>
            caption="Master Data Kebun Petani"
            rows={farms}
            isLoading={farmsQuery.isLoading}
            getRowKey={(row) => row.id}
            columns={[
              {
                key: 'farm',
                header: 'Kebun',
                render: (row) => (
                  <div>
                    <p className="font-mono text-xs font-bold text-primary-default">
                      {row.farm_code}
                    </p>
                    <p className="font-semibold text-ink-primary">{row.farm_name}</p>
                    <p className="text-xs text-text-muted">STDB: {row.stdb_number || '-'}</p>
                  </div>
                ),
              },
              {
                key: 'area',
                header: 'Luas & Tanam',
                align: 'right',
                render: (row) => (
                  <div>
                    <p className="font-mono font-semibold">{formatHectares(row.area_hectares)}</p>
                    <p className="text-xs text-text-muted">Tanam: {row.planting_year ?? '-'}</p>
                  </div>
                ),
              },
              {
                key: 'location',
                header: 'Lokasi',
                render: (row) => (
                  <LocationLink
                    address={row.village || 'Desa terdaftar'}
                    district={row.district}
                    latitude={row.latitude}
                    longitude={row.longitude}
                    hasVerifiedCoordinates={Boolean(row.latitude && row.longitude)}
                  />
                ),
              },
              {
                key: 'actions',
                header: 'Aksi',
                render: (row) =>
                  canWrite ? (
                    <Button size="sm" variant="outline" onClick={() => startEditFarm(row)}>
                      Ubah Kebun
                    </Button>
                  ) : (
                    <span className="text-xs text-text-muted">Hanya baca</span>
                  ),
              },
            ]}
          />
        )}
      </section>

      <ConfirmDialog
        open={Boolean(farmerToToggleStatus)}
        title={
          farmerToToggleStatus?.status === 'ACTIVE'
            ? `Nonaktifkan Petani ${farmerToToggleStatus?.farmer_code}?`
            : `Aktifkan Kembali Petani ${farmerToToggleStatus?.farmer_code}?`
        }
        description="Sesuai BR-023/MD-002, data historis transaksi tidak pernah dihapus melainkan dinonaktifkan dengan alasan tercatat di audit log."
        requireReason
        confirmLabel="Simpan Perubahan Status"
        tone={farmerToToggleStatus?.status === 'ACTIVE' ? 'danger' : 'primary'}
        isSubmitting={updateFarmer.isPending}
        onConfirm={(reason) => handleConfirmToggleFarmerStatus(reason)}
        onCancel={() => setFarmerToToggleStatus(null)}
      />
    </div>
  );
}
