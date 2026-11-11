import { useState } from 'react';
import { Button, Input } from '@/components/atoms';
import { FormField, StatusIndicator } from '@/components/molecules';
import { DataTable, FormSection } from '@/components/organisms';
import { formatKg } from '@/lib/decimal/precision';
import { useUiStore } from '@/lib/state/uiStore';
import {
  useCreateDriver,
  useCreateVehicle,
  useDrivers,
  useVehicles,
  type Driver,
  type Vehicle,
} from '../api/masterDataApi';

export function FleetMasterSection({ canWrite }: { readonly canWrite: boolean }) {
  const pushToast = useUiStore((s) => s.pushToast);
  const vehiclesQuery = useVehicles();
  const driversQuery = useDrivers();
  const createVehicle = useCreateVehicle();
  const createDriver = useCreateDriver();

  const [plateNumber, setPlateNumber] = useState('');
  const [vehicleType, setVehicleType] = useState('Truk Dump 6 Roda');
  const [capacityKg, setCapacityKg] = useState('8000.000');

  const [driverName, setDriverName] = useState('');
  const [driverPhone, setDriverPhone] = useState('');
  const [driverRef, setDriverRef] = useState('');

  const handleAddVehicle = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!plateNumber.trim()) return;
    const res = await createVehicle.mutateAsync({
      plate_number: plateNumber.trim(),
      vehicle_type: vehicleType.trim() || 'Truk',
      nominal_capacity_kg: Number(capacityKg || '8000').toFixed(3),
    });
    pushToast({ tone: 'success', title: `Armada ${res.data.plate_number} ditambahkan.` });
    setPlateNumber('');
  };

  const handleAddDriver = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!driverName.trim() || driverPhone.trim().length < 8) return;
    const res = await createDriver.mutateAsync({
      full_name: driverName.trim(),
      contact_phone: driverPhone.trim(),
      driver_reference: driverRef.trim() || null,
    });
    pushToast({ tone: 'success', title: `Supir ${res.data.full_name} ditambahkan.` });
    setDriverName('');
    setDriverPhone('');
    setDriverRef('');
  };

  return (
    <div className="space-y-6">
      {canWrite ? (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
          <FormSection title="Tambah Kendaraan Pengangkut TBS">
            <form onSubmit={(e) => void handleAddVehicle(e)} className="space-y-3">
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                <FormField id="veh-plate" label="Nomor Polisi" required>
                  <Input
                    id="veh-plate"
                    monospace
                    placeholder="BM 8899 KK"
                    value={plateNumber}
                    onChange={(e) => setPlateNumber(e.target.value)}
                  />
                </FormField>
                <FormField id="veh-type" label="Jenis Truk" required>
                  <Input
                    id="veh-type"
                    value={vehicleType}
                    onChange={(e) => setVehicleType(e.target.value)}
                  />
                </FormField>
                <FormField id="veh-cap" label="Kapasitas (kg)" required>
                  <Input
                    id="veh-cap"
                    monospace
                    value={capacityKg}
                    onChange={(e) => setCapacityKg(e.target.value)}
                  />
                </FormField>
              </div>
              <Button type="submit" isLoading={createVehicle.isPending}>
                Simpan Kendaraan
              </Button>
            </form>
          </FormSection>

          <FormSection title="Tambah Data Supir">
            <form onSubmit={(e) => void handleAddDriver(e)} className="space-y-3">
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
                <FormField id="drv-name" label="Nama Supir" required>
                  <Input
                    id="drv-name"
                    placeholder="Nama lengkap"
                    value={driverName}
                    onChange={(e) => setDriverName(e.target.value)}
                  />
                </FormField>
                <FormField id="drv-phone" label="No. Telepon" required>
                  <Input
                    id="drv-phone"
                    placeholder="081312345678"
                    value={driverPhone}
                    onChange={(e) => setDriverPhone(e.target.value)}
                  />
                </FormField>
                <FormField id="drv-ref" label="Referensi SIM / ID">
                  <Input
                    id="drv-ref"
                    monospace
                    placeholder="DRV-09"
                    value={driverRef}
                    onChange={(e) => setDriverRef(e.target.value)}
                  />
                </FormField>
              </div>
              <Button type="submit" isLoading={createDriver.isPending}>
                Simpan Supir
              </Button>
            </form>
          </FormSection>
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <DataTable<Vehicle>
          caption="Daftar Armada Kendaraan"
          rows={vehiclesQuery.data?.data ?? []}
          isLoading={vehiclesQuery.isLoading}
          getRowKey={(v) => v.id}
          columns={[
            {
              key: 'plate',
              header: 'Plat Nomor',
              render: (v) => <span className="font-mono font-bold">{v.plate_number}</span>,
            },
            { key: 'type', header: 'Jenis', render: (v) => v.vehicle_type },
            {
              key: 'cap',
              header: 'Kapasitas',
              align: 'right',
              render: (v) => <span className="font-mono">{formatKg(v.nominal_capacity_kg)}</span>,
            },
            {
              key: 'status',
              header: 'Status',
              render: (v) => <StatusIndicator status={v.status} />,
            },
          ]}
        />

        <DataTable<Driver>
          caption="Daftar Supir Aktif"
          rows={driversQuery.data?.data ?? []}
          isLoading={driversQuery.isLoading}
          getRowKey={(d) => d.id}
          columns={[
            { key: 'name', header: 'Nama Supir', render: (d) => <span className="font-semibold">{d.full_name}</span> },
            { key: 'phone', header: 'Kontak', render: (d) => d.contact_phone || '-' },
            { key: 'ref', header: 'Referensi', render: (d) => <span className="font-mono text-xs">{d.driver_reference || '-'}</span> },
            { key: 'status', header: 'Status', render: (d) => <StatusIndicator status={d.status} /> },
          ]}
        />
      </div>
    </div>
  );
}
