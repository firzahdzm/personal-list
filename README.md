# Katalog Koleksi Pribadi — Tugas Akhir Struktur Data (GUI)

Program Python berbasis **GUI (Tkinter)** untuk mengelola katalog koleksi
pribadi (Musik, Film, Game, Buku) menggunakan struktur data **Binary Search
Tree (BST)**.

Tiap item koleksi disimpan sebagai satu **node** pohon biner dengan **key =
judul**. Karena setiap node maksimal punya **2 anak** (kiri & kanan) dan
mengikuti aturan urut, program bisa melakukan **pencarian cepat (binary
search, O(log n))** dan **kunjungan preorder / inorder / postorder**.

## Cara Menjalankan

Berkat path yang di-anchor ke lokasi script, program bisa dijalankan dari
folder mana pun:

```bash
/usr/bin/python3 main.py
```

> **Penting di macOS:** Python dari Homebrew (`python3` di Terminal) by default
> **tidak include** modul `_tkinter`. Gunakan **`/usr/bin/python3`** (Python
> bawaan macOS — sudah include Tkinter), atau install via Homebrew:
> ```bash
> brew install python-tk@3.14   # sesuaikan dengan versi python3 di sistemmu
> ```
>
> Cek versi sistem: `python3 --version`

Selain Tkinter (built-in di `/usr/bin/python3`), tidak perlu install library
lain — `ast` dan `pprint` juga sudah bagian dari standar Python.

## Konsep Binary Search Tree

- **Key** tiap node = `judul` (dibandingkan case-insensitive).
- **Aturan urut:** anak `kiri` selalu lebih kecil, anak `kanan` lebih besar
  dari node-nya.
- Akibatnya: **kunjungan inorder otomatis menghasilkan urutan alfabetis**, dan
  pencarian cukup turun ke satu sisi tiap langkah (≈ `log₂ n` perbandingan).

Contoh bentuk pohon (ilustrasi sebagian):

```
              Yellow
             /      \
      Interstellar   Zzz Item Baru
        /     \
   Inception  Skyrim
```

`Inception < Interstellar < Skyrim < Yellow < Zzz` → inorder akan
mengunjunginya tepat dalam urutan itu.

## Struktur File

| File | Isi |
|------|-----|
| `main.py`    | **GUI Tkinter** — class `KatalogApp` + `TambahDialog`, render struktur kiri/kanan. |
| `tree.py`    | `class Node` (`kiri`/`kanan`) & operasi BST rekursif: `sisip`, `cari`, `hapus`, `preorder`, `inorder`, `postorder`, `tinggi`, `hitung`. |
| `storage.py` | Simpan/muat BST ke `koleksi.py`. Serialisasi urutan **preorder** + baca aman pakai `ast.literal_eval`. |
| `koleksi.py` | **Auto-generated.** Berisi `koleksi = [ {judul, tipe, data}, … ]` (list literal Python, urutan preorder). |

## Tampilan

GUI menampilkan **struktur pohon biner** (indentasi = parent→anak, kolom
*Posisi* menandai anak kiri/kanan):

```
┌──────────────────────────────────────────────────────────────────────┐
│ Katalog Koleksi Pribadi — Binary Search Tree                          │
├──────────────────────────────────────────────────────────────────────┤
│ [+ Tambah] [− Hapus] [Cari…] [Traversal] [Statistik] [↻ Refresh]      │
├──────────────────────────────────────────────────────────────────────┤
│ Judul (struktur pohon)     | Posisi  | Tipe  | Detail                 │
│ ▼ Yellow                   | ● akar  | Musik | durasi: 4:29, ...       │
│   ▼ Interstellar           | ↙ kiri  | Film  | tahun: 2014, ...        │
│     • Inception            | ↙ kiri  | Film  | tahun: 2010, ...        │
│     • Skyrim               | ↘ kanan | Game  | rating: 9.0, ...        │
│   • Zzz Item Baru          | ↘ kanan | Buku  | tahun: 2024, ...        │
├──────────────────────────────────────────────────────────────────────┤
│ Total: 38 item | Tinggi pohon: 9 | File: koleksi.py                   │
└──────────────────────────────────────────────────────────────────────┘
```

## Fitur

1. **Tambah** — dialog modal: pilih tipe → field atribut muncul otomatis →
   isi judul (jadi key BST). Atribut divalidasi sesuai tipe (`int`, `float`,
   `str`). Judul duplikat ditolak (key BST harus unik).
2. **Hapus** — pilih node → tombol Hapus (atau tekan `Delete`) → konfirmasi.
   Mengikuti **3 kasus penghapusan BST**: node tanpa anak / satu anak langsung
   disambung; node dua anak diganti **suksesor inorder** (node terkecil di
   subpohon kanan).
3. **Cari** — input judul → **binary search**. Menampilkan item yang ketemu
   beserta **jumlah langkah perbandingan** (bukti efisiensi O(log n)).
   Case-insensitive.
4. **Traversal** — window berisi tiga kunjungan: **preorder** (Akar→Kiri→Kanan),
   **inorder** (Kiri→Akar→Kanan, hasilnya terurut), **postorder**
   (Kiri→Kanan→Akar).
5. **Statistik** — total item, **tinggi pohon**, jumlah per tipe, dan tipe
   terbanyak.
6. **Refresh** — render ulang pohon (berguna kalau `koleksi.py` diedit manual).
7. **Auto-save** — setiap perubahan langsung tersimpan ke `koleksi.py`.

## Operasi BST (`tree.py`)

| Fungsi | Kegunaan |
|--------|----------|
| `sisip(akar, judul, tipe, data)` | Sisip node baru sesuai aturan urut; tolak duplikat. |
| `cari(akar, judul)` | Binary search; return `(node, jumlah_langkah)`. |
| `hapus(akar, judul)` | Hapus node (3 kasus klasik BST). |
| `preorder / inorder / postorder` | Tiga jenis kunjungan pohon biner. |
| `tinggi(akar)` | Tinggi pohon (kosong = 0, satu node = 1). |
| `hitung(akar)` | Jumlah total node. |
| `hitung_per_tipe(akar)` | Jumlah node per tipe (untuk statistik). |

## Komponen Tkinter yang Dipakai

- `ttk.Treeview` — display struktur pohon biner (kolom Posisi / Tipe / Detail).
- `ttk.Combobox` — pilih tipe item (state=readonly).
- `tk.Toplevel` — dialog modal `TambahDialog` & window Traversal.
- `tkinter.messagebox` — konfirmasi hapus, info statistik & pencarian, error validasi.
- `tkinter.simpledialog` — prompt input judul pencarian.
- `tk.StringVar` — binding antara widget dan state Python.

## Catatan Teknis

- **`FILE_DATA` di-anchor ke `__file__`** (bukan path relatif), jadi aman
  dijalankan dari direktori mana pun.
- **Pemuatan data pakai `ast.literal_eval`** (bukan `exec`) — lebih aman karena
  file hanya boleh berisi literal, bukan kode arbitrer.
- **Serialisasi urutan preorder:** saat dimuat ulang, item disisipkan dengan
  urutan yang sama sehingga **bentuk pohon ter-rekonstruksi persis** (tidak
  berubah/menggepeng).
- Ini **BST sederhana** (belum self-balancing seperti AVL) — sesuai cakupan
  materi binary tree dasar.
