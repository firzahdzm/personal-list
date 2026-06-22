# Pemandu Pesan Menu — Tugas Akhir Struktur Data (GUI)

Program Python berbasis **GUI (Tkinter)** untuk membantu pelanggan restoran
memilih menu, menggunakan struktur data **Pohon Keputusan (binary decision
tree)**.

Pelanggan menjawab pertanyaan **ya / tidak** dan menelusuri pohon biner sampai
ketemu **menu** yang direkomendasikan. Tiap node pertanyaan punya **tepat 2
cabang** (ya = kiri, tidak = kanan) — jadi struktur binary tree-nya bermakna
& gampang dimengerti (tiap pertanyaan membelah pilihan jadi dua).

Program **mulai dari kosong** dan dibangun lewat interaksi. Saat dibuka ada
**layar Beranda** untuk memilih mode:
- **🍽 Coba Pesan** — jalankan pemandu (jawab ya/tidak → menu rekomendasi).
- **🔧 Kelola Menu** — bangun & edit pohon menu dari nol.

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
- **Pertanyaan** (node internal) → punya 2 anak (kiri & kanan). Label tiap
  cabang bisa **di-custom** (mis. "Pedas" / "Manis"), default "Ya" / "Tidak".
  Tetap 2 cabang → tetap binary tree.
- **Menu** (daun) → tidak punya anak; menyimpan `nama`, `harga`, `deskripsi`.

Contoh pohon yang bisa kamu bangun (program sendiri mulai kosong):

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
| `main.py`    | **GUI Tkinter** — `class App` (3 layar: Beranda / Kelola / Coba), diagram canvas, dialog, guard Tk. |
| `tree.py`    | `class Node` (`ya`/`tidak`) & operasi pohon: traversal, `tinggi`, `hitung_menu`, `hitung_pertanyaan`, `jadikan_pertanyaan`, `hapus`. |
| `storage.py` | Simpan/muat pohon ke `menu.py` sebagai nested dict + baca aman `ast.literal_eval`. |
| `menu.py`    | **Auto-generated.** `menu = None` saat kosong; jadi `menu = { ... }` (nested ya/tidak) setelah kamu membangun. |

## Tampilan

Program punya **3 layar** dalam satu jendela.

**① Beranda** — pilih mode begitu dibuka:

```
           🍴  Pemandu Pesan Menu
   ┌───────────────┐   ┌───────────────┐
   │ 🍽 Coba Pesan │   │ 🔧 Kelola Menu│
   │   (pemandu)   │   │ (bangun pohon)│
   └───────────────┘   └───────────────┘
```

**② Kelola Menu** — bangun pohon (mulai kosong → **[➕ Buat Menu Pertama]**,
lalu **Pecah jadi Pertanyaan**). Diagram di canvas: 🟦 pertanyaan, 🟨 menu,
cabang **kiri = Ya / kanan = Tidak**. **Klik node** untuk memilih (Edit/Hapus/Pecah).

**③ Coba Pesan** — diagram pohon + panel Q&A; jawab Ya/Tidak, **jalur ter-sorot
hijau**, berhenti di menu rekomendasi:

```
   [ Suka pedas? ]           ┌─── Coba Pesan ───┐
   ya /      \ tidak         │ Suka pedas?      │
 «Ayam      «Nasi            │   [  ✓ Ya  ]     │
 Geprek»    Goreng»          │   [ ✗ Tidak ]    │
 (kuning = menu + harga)     └──────────────────┘
```

## Fitur

**Beranda** — pilih **Coba Pesan** atau **Kelola Menu**.

**Mode Kelola Menu** (bangun dari kosong):
1. **Buat Menu Pertama** — saat kosong, buat satu menu (nama, harga, deskripsi).
2. **Pecah jadi Pertanyaan** — pilih node menu → jadikan pertanyaan dengan 2
   pilihan + **label cabang custom** (menu lama tetap, menu baru ditambah).
   Cara pohon "tumbuh".
3. **Edit** — ubah teks pertanyaan & **label tiap cabangnya**, atau
   nama/harga/deskripsi menu.
4. **Hapus** — node biasa: induk **runtuh**, saudaranya naik; menu terakhir →
   pohon kembali kosong.
5. **Traversal** (preorder/inorder/postorder) & **Statistik** (jumlah menu &
   pertanyaan, tinggi pohon).

**Mode Coba Pesan:**
6. **Pandu Pesan** — jawab **Ya/Tidak** langkah demi langkah; **jalur ter-sorot
   hijau** di diagram pohon; berhenti di **menu rekomendasi** (nama, harga, deskripsi).

**Auto-save** — tiap perubahan langsung tersimpan ke `menu.py`.

## Operasi Pohon (`tree.py`)

| Fungsi | Kegunaan |
|--------|----------|
| `jadikan_pertanyaan(node, tanya, menu_ya, menu_tidak)` | Pecah daun menu jadi pertanyaan + 2 daun. |
| `hapus(akar, target)` | Hapus node; induk runtuh, saudara naik (return `(akar, ok)`). |
| `preorder / inorder / postorder` | Tiga jenis kunjungan pohon biner. |
| `tinggi(node)` | Tinggi pohon (kosong = 0). |
| `hitung_menu(node)` / `hitung_pertanyaan(node)` | Jumlah daun / node internal. |

## Komponen Tkinter yang Dipakai

- `tk.Canvas` — menggambar diagram pohon (kotak node + cabang ya/tidak), klik untuk memilih node.
- `ttk.Combobox` — pilih cabang (ya/tidak) saat menambah cabang.
- `tk.Toplevel` — dialog Tambah/Edit & window Traversal.
- `tkinter.messagebox` — konfirmasi, info, peringatan versi Tk.
- `tk.StringVar` — binding widget ↔ state Python.

## Catatan Teknis

- **`FILE_DATA` di-anchor ke `__file__`** — aman dijalankan dari folder mana pun.
- **Pemuatan data pakai `ast.literal_eval`** (bukan `exec`) — lebih aman.
- **Serialisasi nested dict** merekam cabang `ya`/`tidak` tiap node, jadi bentuk
  pohon ter-rekonstruksi persis saat dimuat ulang.
- **Guard versi Tk** memperingatkan kalau Tk < 8.6 (penyebab jendela hitam di
  macOS baru).
