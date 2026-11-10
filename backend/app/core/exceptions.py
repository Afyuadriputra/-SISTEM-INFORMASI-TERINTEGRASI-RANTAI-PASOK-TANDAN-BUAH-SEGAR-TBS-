"""Pure canonical error codes and domain-safe AppError (framework-free)."""

from __future__ import annotations

from enum import StrEnum
from typing import Any


class ErrorCode(StrEnum):
    """Canonical error codes aligned 1:1 with contracts/error-catalog.yaml."""

    AUTH_INVALID_CREDENTIALS = "AUTH_INVALID_CREDENTIALS"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    AUTH_SESSION_EXPIRED = "AUTH_SESSION_EXPIRED"
    AUTH_CSRF_INVALID = "AUTH_CSRF_INVALID"
    AUTH_TOO_MANY_REQUESTS = "AUTH_TOO_MANY_REQUESTS"
    AUTH_ACCESS_DENIED = "AUTH_ACCESS_DENIED"
    AUTH_SCOPE_FORBIDDEN = "AUTH_SCOPE_FORBIDDEN"
    AUTH_OPERATION_FORBIDDEN = "AUTH_OPERATION_FORBIDDEN"
    AUTH_CONFLICT_OF_DUTIES = "AUTH_CONFLICT_OF_DUTIES"
    SYS_RESOURCE_NOT_FOUND = "SYS_RESOURCE_NOT_FOUND"
    VAL_REQUIRED_FIELD = "VAL_REQUIRED_FIELD"
    VAL_INVALID_FORMAT = "VAL_INVALID_FORMAT"
    VAL_INVALID_DECIMAL_PRECISION = "VAL_INVALID_DECIMAL_PRECISION"
    VAL_INVALID_COORDINATES = "VAL_INVALID_COORDINATES"
    VAL_INVALID_DATE_RANGE = "VAL_INVALID_DATE_RANGE"
    MD_DUPLICATE_CODE = "MD_DUPLICATE_CODE"
    MD_ENTITY_IN_USE = "MD_ENTITY_IN_USE"
    MD_STALE_RECORD_VERSION = "MD_STALE_RECORD_VERSION"
    PRICE_INVALID_AMOUNT = "PRICE_INVALID_AMOUNT"
    PRICE_INVALID_PERIOD = "PRICE_INVALID_PERIOD"
    PRICE_NOT_VERIFIED = "PRICE_NOT_VERIFIED"
    PRICE_ALREADY_PUBLISHED = "PRICE_ALREADY_PUBLISHED"
    PRICE_OVERLAPPING_PERIOD = "PRICE_OVERLAPPING_PERIOD"
    PRICE_INVALID_STATE_TRANSITION = "PRICE_INVALID_STATE_TRANSITION"
    TBS_INVALID_WEIGHT = "TBS_INVALID_WEIGHT"
    TBS_INVALID_GRADING_DEDUCTION = "TBS_INVALID_GRADING_DEDUCTION"
    TBS_DUPLICATE_RECEIPT = "TBS_DUPLICATE_RECEIPT"
    TBS_RECEIPT_LOCKED = "TBS_RECEIPT_LOCKED"
    TBS_INVALID_STATE_TRANSITION = "TBS_INVALID_STATE_TRANSITION"
    TBS_STALE_RECORD_VERSION = "TBS_STALE_RECORD_VERSION"
    CONTRACT_NOT_ACTIVE = "CONTRACT_NOT_ACTIVE"
    CONTRACT_EXPIRED = "CONTRACT_EXPIRED"
    CONTRACT_QUOTA_EXCEEDED = "CONTRACT_QUOTA_EXCEEDED"
    CONTRACT_CONCURRENT_CONFLICT = "CONTRACT_CONCURRENT_CONFLICT"
    CONTRACT_BUSINESS_MODEL_UNCONFIRMED = "CONTRACT_BUSINESS_MODEL_UNCONFIRMED"
    LOG_DELIVERY_ALREADY_ASSIGNED = "LOG_DELIVERY_ALREADY_ASSIGNED"
    LOG_INVALID_STATE_TRANSITION = "LOG_INVALID_STATE_TRANSITION"
    LOG_CANCELLATION_FORBIDDEN = "LOG_CANCELLATION_FORBIDDEN"
    LOG_QR_VERIFICATION_FAILED = "LOG_QR_VERIFICATION_FAILED"
    LOG_STALE_RECORD_VERSION = "LOG_STALE_RECORD_VERSION"
    IDM_KEY_CONFLICT_PAYLOAD_MISMATCH = "IDM_KEY_CONFLICT_PAYLOAD_MISMATCH"
    IDM_REQUEST_IN_PROGRESS = "IDM_REQUEST_IN_PROGRESS"
    MILL_EDO_MILL_MISMATCH = "MILL_EDO_MILL_MISMATCH"
    MILL_DUPLICATE_TICKET = "MILL_DUPLICATE_TICKET"
    MILL_EDO_NOT_ELIGIBLE = "MILL_EDO_NOT_ELIGIBLE"
    MILL_TICKET_ALREADY_FINAL = "MILL_TICKET_ALREADY_FINAL"
    REC_NOT_READY = "REC_NOT_READY"
    REC_INVALID_WEIGHT_BASIS = "REC_INVALID_WEIGHT_BASIS"
    REC_WEIGHT_DISPUTE = "REC_WEIGHT_DISPUTE"
    REC_NEGATIVE_DIFFERENCE_HOLD = "REC_NEGATIVE_DIFFERENCE_HOLD"
    REC_DISPUTE_REASON_REQUIRED = "REC_DISPUTE_REASON_REQUIRED"
    REC_INVALID_STATE_TRANSITION = "REC_INVALID_STATE_TRANSITION"
    REC_ALLOCATION_IMBALANCE = "REC_ALLOCATION_IMBALANCE"
    REC_ALLOCATION_POLICY_UNCONFIRMED = "REC_ALLOCATION_POLICY_UNCONFIRMED"
    FIN_INVOICE_NOT_VERIFIED = "FIN_INVOICE_NOT_VERIFIED"
    FIN_DISPUTE_HOLD_BLOCKED = "FIN_DISPUTE_HOLD_BLOCKED"
    FIN_POLICY_UNCONFIRMED = "FIN_POLICY_UNCONFIRMED"
    PAY_APPROVAL_REQUIRED = "PAY_APPROVAL_REQUIRED"
    PAY_ALREADY_APPROVED = "PAY_ALREADY_APPROVED"
    PAY_DUPLICATE_PAYMENT = "PAY_DUPLICATE_PAYMENT"
    PAY_PARTIAL_NOT_SUPPORTED = "PAY_PARTIAL_NOT_SUPPORTED"
    PAY_AMOUNT_EXCEEDS_INVOICE = "PAY_AMOUNT_EXCEEDS_INVOICE"
    PAY_PROOF_REQUIRED = "PAY_PROOF_REQUIRED"
    PAY_INVALID_PARTY_PAIRING = "PAY_INVALID_PARTY_PAIRING"
    PAY_INVALID_STATE_TRANSITION = "PAY_INVALID_STATE_TRANSITION"
    SYS_RATE_LIMIT_EXCEEDED = "SYS_RATE_LIMIT_EXCEEDED"
    SYS_DEPENDENCY_UNAVAILABLE = "SYS_DEPENDENCY_UNAVAILABLE"
    SYS_REQUEST_TIMEOUT = "SYS_REQUEST_TIMEOUT"
    SYS_INTERNAL_ERROR = "SYS_INTERNAL_ERROR"


ERROR_CATALOG_DEFAULTS: dict[ErrorCode, tuple[int, str]] = {
    ErrorCode.AUTH_INVALID_CREDENTIALS: (401, "Username atau kata sandi tidak sesuai."),
    ErrorCode.AUTH_REQUIRED: (401, "Silakan masuk terlebih dahulu untuk mengakses layanan ini."),
    ErrorCode.AUTH_SESSION_EXPIRED: (401, "Sesi Anda telah berakhir. Silakan masuk kembali."),
    ErrorCode.AUTH_CSRF_INVALID: (
        403,
        "Permintaan tidak dapat diverifikasi secara aman. Muat ulang halaman lalu coba kembali.",
    ),
    ErrorCode.AUTH_TOO_MANY_REQUESTS: (
        429,
        "Terlalu banyak percobaan masuk. Tunggu beberapa saat sebelum mencoba kembali.",
    ),
    ErrorCode.AUTH_ACCESS_DENIED: (
        403,
        "Anda tidak memiliki izin untuk mengakses atau menjalankan tindakan ini.",
    ),
    ErrorCode.AUTH_SCOPE_FORBIDDEN: (
        403,
        "Anda tidak berwenang mengakses data di luar cakupan organisasi Anda.",
    ),
    ErrorCode.AUTH_OPERATION_FORBIDDEN: (
        403,
        "Peran Anda tidak diperbolehkan melakukan tindakan persetujuan atau perubahan operasional ini.",
    ),
    ErrorCode.AUTH_CONFLICT_OF_DUTIES: (
        403,
        "Tindakan pemeriksaan atau persetujuan harus dilakukan oleh petugas berwenang yang berbeda dari pembuat data.",
    ),
    ErrorCode.SYS_RESOURCE_NOT_FOUND: (404, "Data yang diminta tidak ditemukan."),
    ErrorCode.VAL_REQUIRED_FIELD: (
        422,
        "Data wajib belum lengkap. Periksa bidang yang ditandai.",
    ),
    ErrorCode.VAL_INVALID_FORMAT: (
        422,
        "Format masukan tidak valid. Periksa kembali isian Anda.",
    ),
    ErrorCode.VAL_INVALID_DECIMAL_PRECISION: (
        422,
        "Nilai angka atau presisi desimal tidak valid.",
    ),
    ErrorCode.VAL_INVALID_COORDINATES: (
        422,
        "Koordinat lokasi tidak valid. Latitude (-90 s.d. 90) dan Longitude (-180 s.d. 180) wajib diisi berpasangan.",
    ),
    ErrorCode.VAL_INVALID_DATE_RANGE: (
        422,
        "Periode tanggal tidak valid. Tanggal akhir tidak boleh mendahului tanggal mulai.",
    ),
    ErrorCode.MD_DUPLICATE_CODE: (
        409,
        "Kode referensi sudah terdaftar di sistem. Gunakan kode unik yang berbeda.",
    ),
    ErrorCode.MD_ENTITY_IN_USE: (
        409,
        "Data tidak dapat dihapus karena telah memiliki riwayat transaksi. Gunakan status Nonaktif.",
    ),
    ErrorCode.MD_STALE_RECORD_VERSION: (
        409,
        "Data telah diperbarui oleh pengguna lain. Muat ulang data terbaru sebelum menyimpan.",
    ),
    ErrorCode.PRICE_INVALID_AMOUNT: (
        422,
        "Harga TBS harus lebih besar dari nol rupiah per kilogram.",
    ),
    ErrorCode.PRICE_INVALID_PERIOD: (
        422,
        "Periode berlaku harga tidak sah. Periksa tanggal mulai dan tanggal berakhir.",
    ),
    ErrorCode.PRICE_NOT_VERIFIED: (
        409,
        "Harga belum diverifikasi sehingga belum dapat dipublikasikan.",
    ),
    ErrorCode.PRICE_ALREADY_PUBLISHED: (
        409,
        "Harga ini sudah dipublikasikan dan tidak dapat diubah langsung.",
    ),
    ErrorCode.PRICE_OVERLAPPING_PERIOD: (
        409,
        "Periode berlaku harga bertumpang tindih dengan harga aktif yang sudah dipublikasikan pada kategori PKS ini.",
    ),
    ErrorCode.PRICE_INVALID_STATE_TRANSITION: (
        409,
        "Status harga saat ini tidak mengizinkan tindakan tersebut.",
    ),
    ErrorCode.TBS_INVALID_WEIGHT: (
        422,
        "Nilai timbangan tidak valid: berat tara tidak boleh melebihi berat bruto dan tidak boleh bernilai negatif.",
    ),
    ErrorCode.TBS_INVALID_GRADING_DEDUCTION: (
        422,
        "Rincian potongan mutu tidak valid atau terdeteksi ganda pada komponen yang sama.",
    ),
    ErrorCode.TBS_DUPLICATE_RECEIPT: (
        409,
        "Transaksi penerimaan TBS dengan nomor tersebut sudah tercatat.",
    ),
    ErrorCode.TBS_RECEIPT_LOCKED: (
        409,
        "Transaksi penerimaan sudah masuk pengiriman aktif sehingga terkunci. Gunakan prosedur koreksi resmi.",
    ),
    ErrorCode.TBS_INVALID_STATE_TRANSITION: (
        409,
        "Penerimaan TBS belum memenuhi syarat untuk perpindahan status ini.",
    ),
    ErrorCode.TBS_STALE_RECORD_VERSION: (
        409,
        "Catatan penerimaan ini baru saja diperbarui oleh proses lain. Muat ulang data terbaru.",
    ),
    ErrorCode.CONTRACT_NOT_ACTIVE: (
        409,
        "Kontrak belum aktif atau sedang ditangguhkan sehingga belum dapat digunakan untuk pengiriman.",
    ),
    ErrorCode.CONTRACT_EXPIRED: (
        409,
        "Masa berlaku kontrak atau periode kuota telah berakhir.",
    ),
    ErrorCode.CONTRACT_QUOTA_EXCEEDED: (
        409,
        "Pengiriman belum dapat diterbitkan karena sisa kuota kontrak tidak mencukupi.",
    ),
    ErrorCode.CONTRACT_CONCURRENT_CONFLICT: (
        409,
        "Kuota kontrak sedang diproses transaksi lain secara bersamaan. Muat ulang sisa kuota dan coba kembali.",
    ),
    ErrorCode.CONTRACT_BUSINESS_MODEL_UNCONFIRMED: (
        422,
        "Struktur pihak pada kontrak tidak sesuai dengan klasifikasi model usaha yang dipilih.",
    ),
    ErrorCode.LOG_DELIVERY_ALREADY_ASSIGNED: (
        409,
        "Sebagian muatan penerimaan sudah dialokasikan ke e-DO aktif lain dan tidak dapat dikirim ganda.",
    ),
    ErrorCode.LOG_INVALID_STATE_TRANSITION: (
        409,
        "Status pengiriman saat ini tidak dapat diubah ke status tujuan tersebut.",
    ),
    ErrorCode.LOG_CANCELLATION_FORBIDDEN: (
        409,
        "Pengiriman yang sudah tiba atau diterima di PKS tidak dapat dibatalkan langsung.",
    ),
    ErrorCode.LOG_QR_VERIFICATION_FAILED: (
        404,
        "Referensi e-DO atau kode QR tidak ditemukan atau sudah dibatalkan.",
    ),
    ErrorCode.LOG_STALE_RECORD_VERSION: (
        409,
        "Status e-DO telah diperbarui pengguna lain. Muat ulang data terbaru.",
    ),
    ErrorCode.IDM_KEY_CONFLICT_PAYLOAD_MISMATCH: (
        409,
        "Kunci idempotensi permintaan sudah digunakan untuk data transaksi yang berbeda. Muat ulang formulir.",
    ),
    ErrorCode.IDM_REQUEST_IN_PROGRESS: (
        409,
        "Permintaan sebelumnya masih diproses. Tunggu sebentar dan periksa status transaksi terkini.",
    ),
    ErrorCode.MILL_EDO_MILL_MISMATCH: (
        403,
        "Dokumen e-DO ini tidak ditujukan untuk PKS Anda.",
    ),
    ErrorCode.MILL_DUPLICATE_TICKET: (
        409,
        "Nomor tiket timbang sudah terdaftar. Periksa kembali nomor tiket sebelum menyimpan.",
    ),
    ErrorCode.MILL_EDO_NOT_ELIGIBLE: (
        409,
        "e-DO belum berstatus tiba di PKS atau telah dibatalkan sehingga tiket timbang belum dapat dicatat.",
    ),
    ErrorCode.MILL_TICKET_ALREADY_FINAL: (
        409,
        "Tiket timbang tidak dapat direvisi langsung karena transaksi keuangan terkait sudah diterbitkan.",
    ),
    ErrorCode.REC_NOT_READY: (
        409,
        "Rekonsiliasi belum dapat dijalankan karena tiket timbang PKS belum tersedia atau belum terverifikasi.",
    ),
    ErrorCode.REC_INVALID_WEIGHT_BASIS: (
        422,
        "Dasar berat asal dan berat PKS tidak setara atau bernilai nol sehingga rekonsiliasi normal ditahan.",
    ),
    ErrorCode.REC_WEIGHT_DISPUTE: (
        409,
        "Selisih berat melebihi toleransi yang berlaku. Transaksi ditahan untuk pemeriksaan sengketa.",
    ),
    ErrorCode.REC_NEGATIVE_DIFFERENCE_HOLD: (
        409,
        "Terdeteksi selisih negatif (berat PKS lebih besar dari berat asal). Transaksi ditahan untuk pemeriksaan anomali.",
    ),
    ErrorCode.REC_DISPUTE_REASON_REQUIRED: (
        422,
        "Alasan pemeriksaan dan keputusan penyelesaian sengketa wajib diisi.",
    ),
    ErrorCode.REC_INVALID_STATE_TRANSITION: (
        409,
        "Status rekonsiliasi saat ini tidak mengizinkan tindakan tersebut.",
    ),
    ErrorCode.REC_ALLOCATION_IMBALANCE: (
        422,
        "Jumlah pembagian alokasi petani tidak seimbang dengan total nilai transaksi yang disahkan.",
    ),
    ErrorCode.REC_ALLOCATION_POLICY_UNCONFIRMED: (
        409,
        "Pembagian hasil final belum dapat disahkan sebelum SOP metode alokasi multi-petani ditetapkan secara resmi.",
    ),
    ErrorCode.FIN_INVOICE_NOT_VERIFIED: (
        409,
        "Faktur belum terverifikasi atau diterbitkan sehingga proses lanjutan belum dapat dijalankan.",
    ),
    ErrorCode.FIN_DISPUTE_HOLD_BLOCKED: (
        409,
        "Transaksi masih dalam pemeriksaan sengketa sehingga faktur atau pembayaran final ditahan.",
    ),
    ErrorCode.FIN_POLICY_UNCONFIRMED: (
        409,
        "Finalisasi keuangan ditahan karena klasifikasi model usaha kontrak (Principal/Agent) belum disahkan.",
    ),
    ErrorCode.PAY_APPROVAL_REQUIRED: (
        409,
        "Pembayaran belum disetujui pejabat berwenang sehingga pencatatan pembayaran belum dapat diproses.",
    ),
    ErrorCode.PAY_ALREADY_APPROVED: (
        409,
        "Permintaan persetujuan pembayaran untuk faktur ini sudah diputuskan sebelumnya.",
    ),
    ErrorCode.PAY_DUPLICATE_PAYMENT: (
        409,
        "Referensi pembayaran sudah pernah tercatat atau kewajiban faktur sudah lunas.",
    ),
    ErrorCode.PAY_PARTIAL_NOT_SUPPORTED: (
        422,
        "Pembayaran sebagian belum didukung pada kebijakan sistem saat ini. Masukkan nominal pelunasan penuh sesuai nilai faktur.",
    ),
    ErrorCode.PAY_AMOUNT_EXCEEDS_INVOICE: (
        422,
        "Nominal pembayaran harus positif dan tidak boleh melebihi total tagihan faktur.",
    ),
    ErrorCode.PAY_PROOF_REQUIRED: (
        422,
        "Bukti dan referensi pembayaran yang sah wajib tersedia sebelum verifikasi pelunasan.",
    ),
    ErrorCode.PAY_INVALID_PARTY_PAIRING: (
        422,
        "Arah pembayaran dan identitas pihak pembayar/penerima tidak sesuai dengan dokumen faktur terkait.",
    ),
    ErrorCode.PAY_INVALID_STATE_TRANSITION: (
        409,
        "Status catatan pembayaran saat ini tidak dapat diproses ulang dengan tindakan tersebut.",
    ),
    ErrorCode.SYS_RATE_LIMIT_EXCEEDED: (
        429,
        "Permintaan terlalu cepat. Tunggu sejenak sebelum mencoba lagi.",
    ),
    ErrorCode.SYS_DEPENDENCY_UNAVAILABLE: (
        503,
        "Layanan sistem sedang mengalami gangguan sementara. Silakan coba lagi beberapa saat atau laporkan kode referensi.",
    ),
    ErrorCode.SYS_REQUEST_TIMEOUT: (
        504,
        "Permintaan membutuhkan waktu terlalu lama. Periksa status transaksi sebelum mencoba mengirim ulang.",
    ),
    ErrorCode.SYS_INTERNAL_ERROR: (
        500,
        "Terjadi kendala pada sistem. Silakan coba kembali atau hubungi administrator dengan kode referensi yang ditampilkan.",
    ),
}


class AppError(Exception):
    """Controlled domain, security, validation, or infrastructure exception."""

    def __init__(
        self,
        code: ErrorCode,
        message: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | list[Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        default_status, default_msg = ERROR_CATALOG_DEFAULTS[code]
        self.code = code
        self.status_code = status_code if status_code is not None else default_status
        self.message = message if message is not None else default_msg
        self.details = details
        self.headers = headers or {}
        super().__init__(self.message)
