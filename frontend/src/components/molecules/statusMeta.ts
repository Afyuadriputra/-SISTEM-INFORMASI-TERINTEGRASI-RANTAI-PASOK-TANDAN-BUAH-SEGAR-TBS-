import type { BadgeTone } from '@/components/atoms';

export interface StatusAppearance {
  readonly label: string;
  readonly tone: BadgeTone;
}

const STATUS_APPEARANCE_MAP: Record<string, StatusAppearance> = {
  // General & Master Data
  ACTIVE: { label: 'Aktif', tone: 'success' },
  INACTIVE: { label: 'Nonaktif', tone: 'neutral' },
  LOCKED: { label: 'Terkunci', tone: 'danger' },
  VERIFIED: { label: 'Terverifikasi', tone: 'success' },
  PENDING: { label: 'Menunggu Verifikasi', tone: 'warning' },
  REJECTED: { label: 'Ditolak', tone: 'danger' },

  // SM-01 Price Quote & SM-03 Contract & SM-09 Invoice shared keys
  DRAFT: { label: 'Draf', tone: 'neutral' },
  PENDING_VERIFICATION: { label: 'Menunggu Verifikasi', tone: 'warning' },
  PUBLISHED: { label: 'Dipublikasikan', tone: 'success' },
  REVOKED: { label: 'Dicabut', tone: 'danger' },
  EXPIRED: { label: 'Kedaluwarsa', tone: 'warning' },

  // SM-02 TBS Receipt
  VALIDATED: { label: 'Tervalidasi', tone: 'primary' },
  ALLOCATED: { label: 'Teralokasi ke e-DO', tone: 'info' },
  SHIPPED: { label: 'Dalam Pengiriman', tone: 'info' },
  CLOSED: { label: 'Selesai', tone: 'success' },
  CANCELLED: { label: 'Dibatalkan', tone: 'danger' },

  // SM-03 Trade Contract & SM-10 Approval
  PENDING_APPROVAL: { label: 'Menunggu Persetujuan', tone: 'warning' },
  SUSPENDED: { label: 'Ditangguhkan', tone: 'warning' },
  COMPLETED: { label: 'Selesai', tone: 'success' },

  // SM-04 Quota Reservation
  RESERVED: { label: 'Tercadang', tone: 'info' },
  CONSUMED: { label: 'Terealisasi', tone: 'success' },
  RELEASED: { label: 'Dilepas', tone: 'neutral' },

  // SM-05 Delivery Order (e-DO)
  READY: { label: 'Siap Kirim / Siap Hitung', tone: 'primary' },
  IN_TRANSIT: { label: 'Dalam Perjalanan', tone: 'info' },
  ARRIVED: { label: 'Tiba di PKS', tone: 'info' },
  RECEIVED: { label: 'Diterima PKS', tone: 'primary' },

  // SM-06 Mill Ticket
  SUBMITTED: { label: 'Dikirim ke Rekonsiliasi', tone: 'info' },
  SUPERSEDED_REVISION: { label: 'Diganti Revisi Baru', tone: 'neutral' },

  // SM-07 Reconciliation & SM-08 Dispute
  WAITING_TICKET: { label: 'Menunggu Tiket PKS', tone: 'neutral' },
  MATCHED: { label: 'Cocok (Matched)', tone: 'success' },
  DISPUTE_HOLD: { label: 'Ditahan Sengketa', tone: 'danger' },
  UNDER_REVIEW: { label: 'Dalam Pemeriksaan', tone: 'warning' },
  RESOLVED: { label: 'Sengketa Selesai', tone: 'primary' },
  ANOMALY_NEGATIVE_DIFFERENCE: { label: 'Anomali Selisih Negatif', tone: 'danger' },

  // SM-09 Invoice & SM-10/11 Payment
  ISSUED: { label: 'Diterbitkan', tone: 'primary' },
  VOID: { label: 'Dibatalkan (Void)', tone: 'danger' },
  APPROVED: { label: 'Disetujui', tone: 'success' },
  AWAITING_PAYMENT: { label: 'Menunggu Pembayaran', tone: 'warning' },
  PAID: { label: 'Lunas Terverifikasi', tone: 'success' },
  REVERSED: { label: 'Dibalikkan', tone: 'danger' },

  // Contract Business Models / Classification
  CONFIRMED: { label: 'Ditetapkan Resmi', tone: 'primary' },
  SIMULATION_ONLY: { label: 'Aturan Simulasi', tone: 'warning' },
  PENDING_SOP: { label: 'Menunggu SOP', tone: 'warning' },
  UNCONFIRMED: { label: 'Belum Disahkan', tone: 'warning' },
};

export function resolveStatusAppearance(status: string): StatusAppearance {
  const match = STATUS_APPEARANCE_MAP[status];
  if (match) {
    return match;
  }
  return { label: status.replace(/_/g, ' '), tone: 'neutral' };
}
