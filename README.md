# Buku Telepon — Tugas Akhir Struktur Data (GUI)

Program Python berbasis **GUI (Tkinter)** untuk mengelola buku telepon
menggunakan struktur data **Binary Search Tree (BST)**.

Tiap kontak disimpan sebagai satu **node** pohon biner dengan **key = nama**.
Karena setiap node maksimal punya **2 anak** (kiri & kanan) dan mengikuti
aturan urut, program bisa melakukan **pencarian cepat (binary search,
O(log n))** dan **kunjungan preorder / inorder / postorder**.

> Buku telepon dipilih karena **cocok** dengan binary tree: data flat dengan
> satu key (nama) untuk diurutkan & dicari — beda dengan katalog/playlist yang
> hierarkis (tidak pas untuk binary tree).

## Cara Menjalankan

```bash
/opt/homebrew/bin/python3 main.py
```

> **PENTING — interpreter di macOS:**
> Pakai Python dari **Homebrew** (`/opt/homebrew/bin/python3`) yang memuat
> **Tcl/Tk 9.0**. **JANGAN pakai `/usr/bin/python3`** bawaan macOS — itu
> memakai **Tk 8.5** yang **rusak rendering** di macOS versi baru (jendela
> tampil **hitam/blank**).
>
> Program sudah punya **guard**: kalau ke-detect Tk < 8.6, muncul peringatan
> berisi saran interpreter yang benar.
>
> Cek versi Tk: `python3 -c "import tkinter; print(tkinter.TkVersion)"`

Selain Tkinter (sudah ada di Homebrew python + `python-tk`), tidak perlu
install library lain — `ast` dan `pprint` bagian dari standar Python.

## Konsep Binary Search Tree

- **Key** tiap node = `nama` (dibandingkan case-insensitive).
- **Aturan urut:** anak `kiri` selalu lebih kecil, anak `kanan` lebih besar.
- Akibatnya: **kunjungan inorder otomatis menghasilkan daftar nama A-Z**, dan
  pencarian cukup turun ke satu sisi tiap langkah (≈ `log₂ n` perbandingan).

Contoh bentuk pohon (ilustrasi sebagian):

```
            Hendra
           /      \
        Budi       Rudi
        /  \        /
     Andi  Citra  Maya
```

`Andi < Budi < Citra < Hendra < Maya < Rudi` → inorder mengunjunginya tepat
dalam urutan itu.

## Struktur File

| File | Isi |
|------|-----|
| `main.py`    | **GUI Tkinter** — class `KatalogApp` + `TambahDialog`, render struktur kiri/kanan, guard versi Tk. |
| `tree.py`    | `class Node` (`kiri`/`kanan`) & operasi BST rekursif: `sisip`, `cari`, `hapus`, `preorder`, `inorder`, `postorder`, `tinggi`, `hitung`. |
| `storage.py` | Simpan/muat BST ke `kontak.py`. Serialisasi urutan **preorder** + baca aman pakai `ast.literal_eval`. |
| `kontak.py`  | **Auto-generated.** Berisi `kontak = [ {nama, nomor, kategori}, … ]` (list literal Python, urutan preorder). |

## Tampilan

GUI menampilkan **struktur pohon biner** (indentasi = parent→anak, kolom
*Posisi* menandai anak kiri/kanan):

```
┌──────────────────────────────────────────────────────────────────────┐
│ Buku Telepon — Binary Search Tree                                     │
├──────────────────────────────────────────────────────────────────────┤
│ [+ Tambah] [− Hapus] [Cari…] [Traversal] [Statistik] [↻ Refresh]      │
├──────────────────────────────────────────────────────────────────────┤
│ Nama (struktur pohon)  | Posisi  | Nomor          | Kategori          │
│ ▼ Hendra               | ● akar  | 0812-1000-2000 | Kerja             │
│   ▼ Budi               | ↙ kiri  | 0856-1111-2222 | Teman             │
│     • Andi             | ↙ kiri  | 0815-2222-3333 | Teman             │
│     • Citra            | ↘ kanan | 0858-4444-5555 | Teman             │
│   ▼ Rudi               | ↘ kanan | 0813-3333-4444 | Kerja             │
│     • Maya             | ↙ kiri  | 0812-9999-0000 | Kerja             │
├──────────────────────────────────────────────────────────────────────┤
│ Total: 18 kontak | Tinggi pohon: 6 | File: kontak.py                  │
└──────────────────────────────────────────────────────────────────────┘
```

## Fitur

1. **Tambah** — dialog modal: isi Nama (jadi key BST), Nomor, Kategori
   (combobox bisa dipilih atau diketik). Nama duplikat ditolak (key BST unik).
2. **Hapus** — pilih kontak → tombol Hapus (atau tekan `Delete`) → konfirmasi.
   Mengikuti **3 kasus penghapusan BST**: node tanpa anak / satu anak langsung
   disambung; node dua anak diganti **suksesor inorder** (node terkecil di
   subpohon kanan).
3. **Cari** — input nama → **binary search**. Menampilkan kontak yang ketemu
   beserta **jumlah langkah perbandingan** (bukti efisiensi O(log n)).
   Case-insensitive.
4. **Traversal** — window berisi tiga kunjungan: **preorder** (Akar→Kiri→Kanan),
   **inorder** (Kiri→Akar→Kanan, hasilnya terurut A-Z), **postorder**
   (Kiri→Kanan→Akar).
5. **Statistik** — total kontak, **tinggi pohon**, jumlah per kategori, dan
   kategori terbanyak.
6. **Refresh** — render ulang pohon (berguna kalau `kontak.py` diedit manual).
7. **Auto-save** — setiap perubahan langsung tersimpan ke `kontak.py`.

## Operasi BST (`tree.py`)

| Fungsi | Kegunaan |
|--------|----------|
| `sisip(akar, nama, nomor, kategori)` | Sisip kontak sesuai aturan urut; tolak duplikat. |
| `cari(akar, nama)` | Binary search; return `(node, jumlah_langkah)`. |
| `hapus(akar, nama)` | Hapus kontak (3 kasus klasik BST). |
| `preorder / inorder / postorder` | Tiga jenis kunjungan pohon biner. |
| `tinggi(akar)` | Tinggi pohon (kosong = 0, satu node = 1). |
| `hitung(akar)` | Jumlah total kontak. |
| `hitung_per_kategori(akar)` | Jumlah kontak per kategori (untuk statistik). |

## Komponen Tkinter yang Dipakai

- `ttk.Treeview` — display struktur pohon biner (kolom Posisi / Nomor / Kategori).
- `ttk.Combobox` — pilih/ketik kategori.
- `tk.Toplevel` — dialog modal `TambahDialog` & window Traversal.
- `tkinter.messagebox` — konfirmasi hapus, info statistik & pencarian, peringatan versi Tk.
- `tkinter.simpledialog` — prompt input nama pencarian.
- `tk.StringVar` — binding antara widget dan state Python.

## Catatan Teknis

- **`FILE_DATA` di-anchor ke `__file__`** (bukan path relatif), jadi aman
  dijalankan dari direktori mana pun.
- **Pemuatan data pakai `ast.literal_eval`** (bukan `exec`) — lebih aman karena
  file hanya boleh berisi literal, bukan kode arbitrer.
- **Serialisasi urutan preorder:** saat dimuat ulang, kontak disisipkan dengan
  urutan yang sama sehingga **bentuk pohon ter-rekonstruksi persis**.
- **Guard versi Tk** di `main.py` memperingatkan kalau Tk < 8.6 (penyebab
  jendela hitam di macOS baru).
- Ini **BST sederhana** (belum self-balancing seperti AVL) — sesuai cakupan
  materi binary tree dasar.
