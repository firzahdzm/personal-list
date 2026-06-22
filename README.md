# Pemandu Pesan Menu — Tugas Akhir Struktur Data (GUI)

Program Python berbasis **GUI (Tkinter)** untuk membantu pelanggan restoran
memilih menu, menggunakan struktur data **Pohon Keputusan (binary decision
tree)**.

Pelanggan menjawab pertanyaan **ya / tidak** dan menelusuri pohon biner sampai
ketemu **menu** yang direkomendasikan. Tiap node pertanyaan punya **tepat 2
cabang** (ya = kiri, tidak = kanan) — jadi struktur binary tree-nya bermakna
& gampang dimengerti (tiap pertanyaan membelah pilihan jadi dua).

## Cara Menjalankan

```bash
/opt/homebrew/bin/python3 main.py
```

> **PENTING — interpreter di macOS:**
> Pakai Python dari **Homebrew** (`/opt/homebrew/bin/python3`, Tk 9.0).
> **JANGAN `/usr/bin/python3`** (Tk 8.5) — rendering-nya rusak di macOS baru
> (jendela tampil **hitam/blank**). Program sudah punya **guard** yang
> memperingatkan kalau Tk < 8.6.
>
> Cek versi Tk: `python3 -c "import tkinter; print(tkinter.TkVersion)"`

Selain Tkinter, tidak perlu library lain (`ast` & `pprint` bawaan Python).

## Konsep Pohon Keputusan

Dua jenis node:
- **Pertanyaan** (node internal) → punya 2 anak: `ya` (kiri) & `tidak` (kanan).
- **Menu** (daun) → tidak punya anak; menyimpan `nama`, `harga`, `deskripsi`.

Contoh pohon default:

```
              Mau makanan berat?
              /ya               \tidak
        Suka pedas?            Mau yang manis?
        /ya      \tidak         /ya         \tidak
   Mau ayam?   Berkuah?   Mau dingin?   Berkafein?
    /ya \tidak  /ya \tidak  /ya \tidak    /ya  \tidak
  Ayam  Mie   Soto  Nasi  Es    Coklat  Kopi  Air
  Geprek Pedas Ayam Goreng Krim  Panas  Hitam Mineral
```

Menjawab **Ya → Ya → Ya** menelusuri: *Mau makanan berat?* → *Suka pedas?* →
*Mau ayam?* → **Ayam Geprek**.

## Struktur File

| File | Isi |
|------|-----|
| `main.py`    | **GUI Tkinter** — `PemanduApp`, fitur Pandu Pesan, dialog Tambah/Edit, guard Tk. |
| `tree.py`    | `class Node` (`ya`/`tidak`) & operasi pohon: traversal, `tinggi`, `hitung_menu`, `hitung_pertanyaan`, `jadikan_pertanyaan`, `hapus`. |
| `storage.py` | Simpan/muat pohon ke `menu.py` sebagai nested dict + baca aman `ast.literal_eval`. |
| `menu.py`    | **Auto-generated.** `menu = { ... }` (struktur pohon biner eksplisit ya/tidak). |

## Tampilan

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Pemandu Pesan Menu — Pohon Keputusan (Binary Tree)                        │
├──────────────────────────────────────────────────────────────────────────┤
│ [🍽 Pandu Pesan] | [+ Tambah Cabang] [✎ Edit] [− Hapus] [Traversal] ...    │
├──────────────────────────────────────────────────────────────────────────┤
│ Pertanyaan / Menu (struktur pohon)  | Jawaban | Jenis      | Harga         │
│ ▼ Mau makanan berat?                | ● akar  | Pertanyaan |               │
│   ▼ Suka pedas?                     | ✓ ya    | Pertanyaan |               │
│     ▼ Mau ayam?                     | ✓ ya    | Pertanyaan |               │
│       • Ayam Geprek                 | ✓ ya    | Menu       | Rp 18.000     │
│       • Mie Goreng Pedas            | ✗ tidak | Menu       | Rp 16.000     │
│   ▼ Mau yang manis?                 | ✗ tidak | Pertanyaan |               │
├──────────────────────────────────────────────────────────────────────────┤
│ Menu: 8 | Pertanyaan: 7 | Tinggi pohon: 4 | File: menu.py                  │
└──────────────────────────────────────────────────────────────────────────┘
```

## Fitur

1. **🍽 Pandu Pesan** — fitur utama. Jawab pertanyaan **Ya/Tidak** langkah demi
   langkah; program menelusuri pohon dan menampilkan **menu rekomendasi** di
   daun (nama, harga, deskripsi). Ada jejak jalur jawaban.
2. **Tambah Cabang** — pilih node **Menu** (daun) → pecah jadi pertanyaan
   dengan 2 pilihan (menu lama dipertahankan, menu baru ditambah). Inilah cara
   pohon "tumbuh".
3. **Edit** — ubah teks pertanyaan, atau nama/harga/deskripsi menu.
4. **Hapus** — hapus node; pertanyaan induknya **runtuh** & cabang saudaranya
   naik menggantikan (analog hapus 1-anak di pohon).
5. **Traversal** — preorder / inorder / postorder seluruh node.
6. **Statistik** — jumlah menu, jumlah pertanyaan, total node, tinggi pohon.
7. **Refresh** + **Auto-save** — perubahan langsung tersimpan ke `menu.py`.

## Operasi Pohon (`tree.py`)

| Fungsi | Kegunaan |
|--------|----------|
| `jadikan_pertanyaan(node, tanya, menu_ya, menu_tidak)` | Pecah daun menu jadi pertanyaan + 2 daun. |
| `hapus(akar, target)` | Hapus node; induk runtuh, saudara naik (return `(akar, ok)`). |
| `preorder / inorder / postorder` | Tiga jenis kunjungan pohon biner. |
| `tinggi(node)` | Tinggi pohon (kosong = 0). |
| `hitung_menu(node)` / `hitung_pertanyaan(node)` | Jumlah daun / node internal. |

## Komponen Tkinter yang Dipakai

- `ttk.Treeview` — display struktur pohon (kolom Jawaban / Jenis / Harga).
- `ttk.Combobox` — pilih cabang (ya/tidak) saat menambah cabang.
- `tk.Toplevel` — dialog Tambah/Edit, window Pandu Pesan & Traversal.
- `tkinter.messagebox` — konfirmasi, info, peringatan versi Tk.
- `tk.StringVar` — binding widget ↔ state Python.

## Catatan Teknis

- **`FILE_DATA` di-anchor ke `__file__`** — aman dijalankan dari folder mana pun.
- **Pemuatan data pakai `ast.literal_eval`** (bukan `exec`) — lebih aman.
- **Serialisasi nested dict** merekam cabang `ya`/`tidak` tiap node, jadi bentuk
  pohon ter-rekonstruksi persis saat dimuat ulang.
- **Guard versi Tk** memperingatkan kalau Tk < 8.6 (penyebab jendela hitam di
  macOS baru).
