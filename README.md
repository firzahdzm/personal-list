# Katalog Koleksi Pribadi — Tugas Akhir Struktur Data (GUI)

Program Python berbasis **GUI (Tkinter)** untuk mengelola katalog koleksi
pribadi (Musik, Film, Game, Buku) menggunakan struktur data **N-ary Tree**.

> Versi CLI tersedia di folder `tugas-akhir-cli/` (sebelahnya).

## Cara Menjalankan

Dari folder `KULIAH/`:
```bash
/usr/bin/python3 smt-02/310--struktur-data/tugas-akhir-gui/main.py
```

> **Penting di macOS:** Python dari Homebrew (`python3` di Terminal) by default
> **tidak include** modul `_tkinter`. Gunakan **`/usr/bin/python3`** (Python
> bawaan macOS — sudah include Tkinter), atau install via Homebrew:
> ```bash
> brew install python-tk@3.14   # sesuaikan dengan versi python3 di sistemmu
> ```
>
> Cek versi sistem: `python3 --version`

Selain Tkinter (yang sudah built-in di Python `/usr/bin/python3`), tidak perlu
install library lain.

## Struktur File

| File | Isi |
|------|-----|
| `main.py`    | **GUI Tkinter** — class `KatalogApp` + `TambahDialog`. |
| `tree.py`    | `class Node` & operasi tree rekursif. **Identik dengan versi CLI.** |
| `storage.py` | Konversi tree ↔ dict & simpan/muat `.py`. **Identik dengan versi CLI.** |
| `koleksi.py` | **Auto-generated.** Berisi `koleksi = {...}` (dict literal Python). |

## Tampilan

```
┌─────────────────────────────────────────────────────────┐
│ Katalog Koleksi Pribadi — N-ary Tree                     │
├─────────────────────────────────────────────────────────┤
│ [+ Tambah]  [− Hapus]  [Cari…]  [Statistik]  [↻ Refresh] │
├─────────────────────────────────────────────────────────┤
│ Nama                              | Detail               │
│ ▼ Koleksi Pribadi                                        │
│   ▼ Musik                                                │
│     ▼ Pop                                                │
│       ▼ Coldplay                                         │
│         • Yellow                  | durasi: 4:29, ...    │
│   ▶ Film                                                 │
│   ▶ Game                                                 │
│   ▶ Buku                                                 │
├─────────────────────────────────────────────────────────┤
│ Total: 1 item | Kedalaman: 4 | File: koleksi.py          │
└─────────────────────────────────────────────────────────┘
```

## Fitur

1. **Tambah** — buka dialog modal. Pilih tipe → form muncul otomatis sesuai
   hierarki tipe. Genre & Platform pakai Combobox (predefined + "Lainnya…"
   untuk input manual). Atribut item divalidasi sesuai tipe (`int`, `float`, `str`).
2. **Hapus** — pilih node di tree → tombol Hapus (atau tekan `Delete`) →
   konfirmasi → cascade delete semua keturunannya.
3. **Cari** — input keyword → window terpisah menampilkan semua hasil dengan
   path lengkapnya. Case-insensitive, partial match.
4. **Statistik** — messagebox dengan total item, kedalaman tree, jumlah per
   tipe, dan tipe terbanyak.
5. **Refresh** — render ulang tree (berguna kalau `koleksi.py` diedit manual).
6. **Auto-save** — setiap perubahan langsung tersimpan ke `koleksi.py`.

## Komponen Tkinter yang Dipakai

- `ttk.Treeview` — display utama tree (dengan kolom Detail).
- `ttk.Combobox` — pilih tipe & genre (state=readonly untuk predefined,
  normal untuk "Lainnya…").
- `tk.Toplevel` — dialog modal `TambahDialog` dan window hasil pencarian.
- `tkinter.messagebox` — konfirmasi hapus, info statistik, error validasi.
- `tkinter.simpledialog` — prompt input keyword pencarian.
- `tk.StringVar` — binding antara widget dan state Python.

## Reuse dengan Versi CLI

`tree.py` dan `storage.py` **identik** dengan versi di `tugas-akhir-cli/` —
inilah keuntungan pemisahan logic dari UI. Class `Node` dan semua operasi
rekursif (`cari_rekursif`, `hitung_item`, `kedalaman_max`, dll.) dipakai ulang
tanpa perubahan apa pun.
