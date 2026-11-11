
Langkah 1 — Buka PowerShell pada root proyek

```
cd "D:\Kuliah\joki\radit\projek thesis bg givo"
```

Langkah 2 — Setup database demo

```
.\scripts\demo-setup.ps1
```

Jalankan saat pertama kali menggunakan demo. Perintah ini aman diulang menurut hasil pengujian; jika data sudah ada, seeder melewati penulisan ulang.

Langkah 3 — Nyalakan seluruh aplikasi

```
.\scripts\demo-start.ps1
```

Launcher akan mengaktifkan backend dan frontend dengan konfigurasi demo yang benar.

Langkah 4 — Buka browser

[http://localhost:5174](http://localhost:5174?utm_source=chatgpt.com)

Alamat yang dipakai pada pengujian terakhir karena port 5173 sedang digunakan aplikasi lain.

Ikuti URL yang ditampilkan launcher. Jika port 5173 sudah kosong, aplikasi dapat menggunakan [http://localhost:5173](http://localhost:5173?utm_source=chatgpt.com).

Langkah 5 — Buka kredensial akun demo

```
notepad ".\backend\.demo-credentials.local.txt"
```

File ini berisi kredensial lokal untuk tujuh peran beserta akun tambahan untuk pengujian. Jangan dibagikan atau dimasukkan ke Git.

Langkah 6 — Hentikan aplikasi setelah selesai

```
.\scripts\demo-stop.ps1
```
