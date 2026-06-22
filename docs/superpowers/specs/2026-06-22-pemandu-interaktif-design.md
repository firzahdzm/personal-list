# Spec — Pemandu Pesan Menu (versi interaktif, mulai kosong)

Tanggal: 2026-06-22

## Tujuan
Membuat program lebih terbaca sebagai **aplikasi yang dijalankan**, dengan
**prioritas interaksi** dan **tanpa data default berlebih**.

## Keputusan desain (disetujui)
1. **Beranda pilih mode** saat dibuka: "Coba Pesan" atau "Kelola Menu".
2. **Mulai kosong total** — pohon dibangun sendiri lewat Kelola.
3. **Coba Pesan tetap menampilkan diagram pohon + menyorot jalur** jawaban.

## Layar (1 jendela, ganti konten)
- **Beranda:** judul + 1 kalimat penjelasan + 2 tombol mode.
- **Kelola Menu:**
  - Kosong → empty-state + tombol **[➕ Buat Menu Pertama]**.
  - Ada isi → diagram canvas + toolbar **[Pecah jadi Pertanyaan] [Edit]
    [Hapus] [Traversal] [Statistik]** + panel detail node.
  - Tombol **[← Beranda]**. Hapus menu terakhir → kembali kosong.
- **Coba Pesan:** diagram pohon + panel Q&A (Ya/Tidak), jalur ter-sorot hijau.
  Jika pohon kosong → arahkan ke Kelola. Tombol **[← Beranda]**.

## Data
`menu.py` berisi `menu = None` (kosong). Tersimpan otomatis saat membangun.

## Operasi membangun dari kosong
- **Buat Menu Pertama** → root = 1 node menu.
- **Pecah jadi Pertanyaan** → menumbuhkan pohon (split daun: menu lama tetap,
  menu baru ditambah).
- **Hapus** root-menu → kosong; root-pertanyaan tidak bisa dihapus.

## Struktur kode
`main.py`: `class App` dengan `tampil_beranda()` / `tampil_kelola()` /
`tampil_coba()` + helper canvas bersama + dialog (BuatMenu, Tambah/split, Edit).
**`tree.py` & `storage.py` tidak diubah.**

## Kriteria sukses
- Buka → beranda jelas (tujuan & cara pakai langsung kebaca).
- Bisa bangun pohon dari nol lalu langsung "Coba Pesan".
- Semua operasi lolos verifikasi (compile + uji headless).

## Di luar lingkup
Animasi transisi, pemecahan ke banyak file, penyeimbangan pohon, fitur lain di
luar daftar di atas.
