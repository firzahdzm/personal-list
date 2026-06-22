"""
main.py
GUI Pemandu Pesan Menu Restoran (Tkinter) berbasis Pohon Keputusan (binary tree).

Satu jendela, tiga layar yang berganti:
  - Beranda      : pilih mode.
  - Kelola Menu  : bangun/edit pohon (mulai dari kosong).
  - Coba Pesan   : jawab ya/tidak, jalur ter-sorot di diagram pohon.

Logika pohon ada di tree.py; penyimpanan di storage.py (tidak diubah).
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox

from tree import (
    Node,
    jadikan_pertanyaan,
    hapus,
    preorder,
    inorder,
    postorder,
    tinggi,
    hitung_menu,
    hitung_pertanyaan,
)
from storage import simpan, muat

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_DATA = os.path.join(BASE_DIR, "menu.py")

# Warna
C_TANYA, C_TANYA_B = "#d6e4ff", "#3a7afe"   # pertanyaan (biru)
C_MENU,  C_MENU_B  = "#fff3cd", "#d9a800"   # menu/daun (kuning)
C_PATH,  C_PATH_B  = "#c8f7c5", "#2e7d32"   # jalur pandu (hijau)
C_SEL_B            = "#e8590c"              # node terpilih (oranye)

# Ukuran layout canvas
BW, BH = 132, 56
SX, SY = 150, 118
MX, MY = 90, 46


def format_rupiah(harga):
    if harga is None:
        return ""
    return "Rp " + f"{harga:,}".replace(",", ".")


# =========================================================================
#  Dialog
# =========================================================================

class BuatMenuDialog:
    """Buat satu node MENU baru (dipakai untuk 'Buat Menu Pertama')."""

    def __init__(self, parent):
        self.berhasil = False
        self.nama = self.harga = self.deskripsi = None

        self.top = tk.Toplevel(parent)
        self.top.title("Buat Menu")
        self.top.geometry("400x290")
        self.top.configure(bg="#f3f3f3")
        self.top.transient(parent)
        self.top.grab_set()

        form = ttk.Frame(self.top, padding=12)
        form.pack(fill=tk.BOTH, expand=True)

        ttk.Label(form, text="Nama menu:", font=("", 10, "bold")).pack(anchor=tk.W)
        self.nama_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.nama_var).pack(fill=tk.X, pady=(2, 8))

        ttk.Label(form, text="Harga (angka, mis. 15000):", font=("", 10, "bold")).pack(anchor=tk.W)
        self.harga_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.harga_var).pack(fill=tk.X, pady=(2, 8))

        ttk.Label(form, text="Deskripsi (opsional):", font=("", 10, "bold")).pack(anchor=tk.W)
        self.desk_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.desk_var).pack(fill=tk.X, pady=(2, 8))

        bf = ttk.Frame(self.top, padding=12)
        bf.pack(fill=tk.X)
        ttk.Button(bf, text="Batal", command=self.top.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(bf, text="Simpan", command=self._simpan).pack(side=tk.RIGHT)

    def _simpan(self):
        nama = self.nama_var.get().strip()
        if not nama:
            messagebox.showerror("Error", "Nama menu tidak boleh kosong.", parent=self.top)
            return
        try:
            harga = int(self.harga_var.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Harga harus berupa angka.", parent=self.top)
            return
        self.nama, self.harga, self.deskripsi = nama, harga, self.desk_var.get().strip()
        self.berhasil = True
        self.top.destroy()


class TambahDialog:
    """Ubah node MENU jadi PERTANYAAN: menu lama tetap di satu cabang, menu
    baru di cabang lainnya."""

    def __init__(self, parent, node_menu):
        self.node = node_menu
        self.berhasil = False

        self.top = tk.Toplevel(parent)
        self.top.title("Pecah jadi Pertanyaan")
        self.top.geometry("440x470")
        self.top.configure(bg="#f3f3f3")
        self.top.transient(parent)
        self.top.grab_set()

        form = ttk.Frame(self.top, padding=12)
        form.pack(fill=tk.BOTH, expand=True)

        ttk.Label(form, text=f"Memecah menu: '{node_menu.teks}'",
                  font=("", 11, "bold")).pack(anchor=tk.W)
        ttk.Label(form, text="Menu ini jadi pertanyaan dengan 2 pilihan.",
                  foreground="#555").pack(anchor=tk.W, pady=(0, 8))

        ttk.Label(form, text="Pertanyaan:", font=("", 10, "bold")).pack(anchor=tk.W)
        self.tanya_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.tanya_var).pack(fill=tk.X, pady=(2, 8))

        ttk.Label(form, text=f"Menu lama '{node_menu.teks}' di cabang:",
                  font=("", 10, "bold")).pack(anchor=tk.W)
        self.posisi_var = tk.StringVar(value="ya")
        ttk.Combobox(form, textvariable=self.posisi_var, values=["ya", "tidak"],
                     state="readonly").pack(fill=tk.X, pady=(2, 8))

        ttk.Separator(form, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=4)
        ttk.Label(form, text="Menu BARU (cabang satunya):",
                  font=("", 10, "bold")).pack(anchor=tk.W, pady=(4, 0))

        ttk.Label(form, text="Nama menu:").pack(anchor=tk.W, pady=(4, 0))
        self.nama_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.nama_var).pack(fill=tk.X)
        ttk.Label(form, text="Harga (angka):").pack(anchor=tk.W, pady=(4, 0))
        self.harga_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.harga_var).pack(fill=tk.X)
        ttk.Label(form, text="Deskripsi:").pack(anchor=tk.W, pady=(4, 0))
        self.desk_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.desk_var).pack(fill=tk.X)

        bf = ttk.Frame(self.top, padding=12)
        bf.pack(fill=tk.X)
        ttk.Button(bf, text="Batal", command=self.top.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(bf, text="Simpan", command=self._simpan).pack(side=tk.RIGHT)

    def _simpan(self):
        tanya = self.tanya_var.get().strip()
        if not tanya:
            messagebox.showerror("Error", "Pertanyaan tidak boleh kosong.", parent=self.top)
            return
        nama = self.nama_var.get().strip()
        if not nama:
            messagebox.showerror("Error", "Nama menu baru tidak boleh kosong.", parent=self.top)
            return
        try:
            harga = int(self.harga_var.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Harga harus berupa angka.", parent=self.top)
            return
        lama = Node(self.node.teks, harga=self.node.harga, deskripsi=self.node.deskripsi)
        baru = Node(nama, harga=harga, deskripsi=self.desk_var.get().strip())
        if self.posisi_var.get() == "ya":
            jadikan_pertanyaan(self.node, tanya, lama, baru)
        else:
            jadikan_pertanyaan(self.node, tanya, baru, lama)
        self.berhasil = True
        self.top.destroy()


class EditDialog:
    def __init__(self, parent, node):
        self.node = node
        self.berhasil = False

        self.top = tk.Toplevel(parent)
        self.top.title("Edit")
        self.top.geometry("420x300")
        self.top.configure(bg="#f3f3f3")
        self.top.transient(parent)
        self.top.grab_set()

        form = ttk.Frame(self.top, padding=12)
        form.pack(fill=tk.BOTH, expand=True)

        is_menu = node.is_menu()
        ttk.Label(form, text=("Nama menu:" if is_menu else "Pertanyaan:"),
                  font=("", 10, "bold")).pack(anchor=tk.W)
        self.teks_var = tk.StringVar(value=node.teks)
        ttk.Entry(form, textvariable=self.teks_var).pack(fill=tk.X, pady=(2, 8))

        self.harga_var = tk.StringVar()
        self.desk_var = tk.StringVar()
        if is_menu:
            ttk.Label(form, text="Harga (angka):", font=("", 10, "bold")).pack(anchor=tk.W)
            self.harga_var.set("" if node.harga is None else str(node.harga))
            ttk.Entry(form, textvariable=self.harga_var).pack(fill=tk.X, pady=(2, 8))
            ttk.Label(form, text="Deskripsi:", font=("", 10, "bold")).pack(anchor=tk.W)
            self.desk_var.set(node.deskripsi)
            ttk.Entry(form, textvariable=self.desk_var).pack(fill=tk.X, pady=(2, 8))

        bf = ttk.Frame(self.top, padding=12)
        bf.pack(fill=tk.X)
        ttk.Button(bf, text="Batal", command=self.top.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(bf, text="Simpan", command=self._simpan).pack(side=tk.RIGHT)

    def _simpan(self):
        teks = self.teks_var.get().strip()
        if not teks:
            messagebox.showerror("Error", "Teks tidak boleh kosong.", parent=self.top)
            return
        if self.node.is_menu():
            try:
                self.node.harga = int(self.harga_var.get().strip())
            except ValueError:
                messagebox.showerror("Error", "Harga harus berupa angka.", parent=self.top)
                return
            self.node.deskripsi = self.desk_var.get().strip()
        self.node.teks = teks
        self.berhasil = True
        self.top.destroy()


# =========================================================================
#  App (3 layar)
# =========================================================================

class App:
    def __init__(self, root_window):
        self.root_window = root_window
        self.root_window.title("Pemandu Pesan Menu — Pohon Keputusan (Binary Tree)")
        self.root_window.geometry("960x620")

        self.akar = muat(FILE_DATA)
        self.selected = None
        self.highlight = set()
        self.node_bbox = {}
        self.pandu_path = []
        self.canvas = None
        self.panel = None

        self.content = ttk.Frame(self.root_window)
        self.content.pack(fill=tk.BOTH, expand=True)

        self.tampil_beranda()

    # ---------- util layar ----------

    def _bersihkan(self):
        for w in self.content.winfo_children():
            w.destroy()
        self.canvas = None
        self.panel = None

    def _reset_state(self):
        self.selected = None
        self.highlight = set()
        self.pandu_path = []

    def _topbar(self, parent, judul):
        bar = ttk.Frame(parent, padding=(8, 6))
        bar.pack(fill=tk.X)
        ttk.Button(bar, text="← Beranda", command=self.tampil_beranda).pack(side=tk.LEFT)
        ttk.Label(bar, text="   " + judul, font=("", 13, "bold")).pack(side=tk.LEFT)
        return bar

    # ---------- Layar: Beranda ----------

    def tampil_beranda(self):
        self._reset_state()
        self._bersihkan()
        wrap = ttk.Frame(self.content, padding=40)
        wrap.pack(expand=True)

        ttk.Label(wrap, text="🍴  Pemandu Pesan Menu", font=("", 22, "bold")).pack(pady=(0, 2))
        ttk.Label(wrap, text="Pohon Keputusan — Binary Tree", foreground="#666").pack()
        ttk.Label(wrap, text="Bantu pelanggan memilih menu lewat pertanyaan ya / tidak.\n"
                             "Pilih mode untuk mulai:",
                  justify=tk.CENTER, foreground="#444").pack(pady=(16, 22))

        baris = ttk.Frame(wrap)
        baris.pack()
        ttk.Button(baris, text="🍽   Coba Pesan\njalankan pemandu", width=22,
                   command=self.tampil_coba).pack(side=tk.LEFT, padx=10, ipady=16)
        ttk.Button(baris, text="🔧   Kelola Menu\nbangun & edit pohon", width=22,
                   command=self.tampil_kelola).pack(side=tk.LEFT, padx=10, ipady=16)

        info = "Total menu: " + str(hitung_menu(self.akar)) if self.akar else "Belum ada menu (kosong)."
        ttk.Label(wrap, text=info, foreground="#888").pack(pady=(22, 0))

    # ---------- Layar: Kelola Menu ----------

    def tampil_kelola(self):
        self._reset_state()
        self._bersihkan()
        self._topbar(self.content, "Kelola Menu")

        if self.akar is None:
            self._kelola_kosong()
            return

        # toolbar
        bar = ttk.Frame(self.content, padding=(8, 4))
        bar.pack(fill=tk.X)
        ttk.Button(bar, text="Pecah jadi Pertanyaan", command=self.aksi_tambah).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="✎ Edit", command=self.aksi_edit).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="− Hapus", command=self.aksi_hapus).pack(side=tk.LEFT, padx=2)
        ttk.Separator(bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=6)
        ttk.Button(bar, text="Traversal", command=self.aksi_traversal).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Statistik", command=self.aksi_statistik).pack(side=tk.LEFT, padx=2)

        # body: canvas + panel detail
        body = ttk.Frame(self.content)
        body.pack(fill=tk.BOTH, expand=True)
        self._buat_canvas(body, clickable=True).pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                                                     padx=(8, 0), pady=(0, 4))
        self.panel = ttk.Frame(body, padding=12, width=260)
        self.panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.panel.pack_propagate(False)

        # statusbar
        self.status_var = tk.StringVar()
        ttk.Label(self.content, textvariable=self.status_var, padding=(8, 4),
                  relief=tk.SUNKEN, anchor=tk.W).pack(fill=tk.X)

        self.gambar_pohon()
        self._tampil_detail(None)
        self._update_status()

    def _kelola_kosong(self):
        wrap = ttk.Frame(self.content, padding=40)
        wrap.pack(expand=True)
        ttk.Label(wrap, text="Belum ada menu apa pun.", font=("", 14, "bold")).pack(pady=(0, 8))
        ttk.Label(wrap, text="Mulai dengan membuat satu menu, lalu pecah jadi\n"
                             "pertanyaan untuk menumbuhkan pohon.",
                  justify=tk.CENTER, foreground="#555").pack(pady=(0, 16))
        ttk.Button(wrap, text="➕  Buat Menu Pertama",
                   command=self.aksi_buat_menu).pack(ipady=8)

    # ---------- Layar: Coba Pesan ----------

    def tampil_coba(self):
        self._reset_state()
        self._bersihkan()
        self._topbar(self.content, "Coba Pesan")

        if self.akar is None:
            wrap = ttk.Frame(self.content, padding=40)
            wrap.pack(expand=True)
            ttk.Label(wrap, text="Belum ada menu untuk dipilih.",
                      font=("", 14, "bold")).pack(pady=(0, 8))
            ttk.Label(wrap, text="Buka 'Kelola Menu' untuk membuat menu & pertanyaan dulu.",
                      foreground="#555").pack(pady=(0, 16))
            ttk.Button(wrap, text="🔧  Ke Kelola Menu", command=self.tampil_kelola).pack(ipady=6)
            return

        body = ttk.Frame(self.content)
        body.pack(fill=tk.BOTH, expand=True)
        self._buat_canvas(body, clickable=False).pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                                                      padx=(8, 0), pady=(0, 6))
        self.panel = ttk.Frame(body, padding=12, width=270)
        self.panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.panel.pack_propagate(False)

        self.pandu_path = []
        self._pandu_render(self.akar)

    # ---------- Canvas (dipakai Kelola & Coba) ----------

    def _buat_canvas(self, parent, clickable):
        wrap = ttk.Frame(parent)
        self.canvas = tk.Canvas(wrap, bg="#ffffff", highlightthickness=1,
                                highlightbackground="#cccccc")
        vs = ttk.Scrollbar(wrap, orient=tk.VERTICAL, command=self.canvas.yview)
        hs = ttk.Scrollbar(wrap, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=vs.set, xscrollcommand=hs.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vs.grid(row=0, column=1, sticky="ns")
        hs.grid(row=1, column=0, sticky="ew")
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)
        if clickable:
            self.canvas.bind("<Button-1>", self._on_click)
        return wrap

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
               x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        return self.canvas.create_polygon(pts, smooth=True, **kw)

    def _hitung_posisi(self):
        pos = {}
        leaf = [0]

        def rek(node, depth):
            if node.is_menu():
                pos[node] = (leaf[0], depth)
                leaf[0] += 1
                return
            rek(node.ya, depth + 1)
            rek(node.tidak, depth + 1)
            pos[node] = ((pos[node.ya][0] + pos[node.tidak][0]) / 2, depth)

        if self.akar is not None:
            rek(self.akar, 0)
        return pos

    def gambar_pohon(self):
        c = self.canvas
        if c is None:
            return
        c.delete("all")
        self.node_bbox = {}
        if self.akar is None:
            return
        pos = self._hitung_posisi()
        px = {n: (MX + x * SX, MY + d * SY) for n, (x, d) in pos.items()}
        for node in pos:
            if node.is_menu():
                continue
            x0, y0 = px[node]
            for child, label, warna in ((node.ya, "ya", C_PATH_B), (node.tidak, "tidak", "#999")):
                x1, y1 = px[child]
                c.create_line(x0, y0 + BH / 2, x1, y1 - BH / 2, fill="#bbbbbb", width=2)
                c.create_text((x0 + x1) / 2, (y0 + y1) / 2 - 6, text=label,
                              fill=warna, font=("", 9, "bold"))
        for node, (x, y) in px.items():
            self._gambar_node(node, x, y)
        c.configure(scrollregion=c.bbox("all"))

    def _gambar_node(self, node, cx, cy):
        x1, y1, x2, y2 = cx - BW / 2, cy - BH / 2, cx + BW / 2, cy + BH / 2
        fill, outline = (C_MENU, C_MENU_B) if node.is_menu() else (C_TANYA, C_TANYA_B)
        width = 2
        if node in self.highlight:
            fill, outline, width = C_PATH, C_PATH_B, 3
        if node is self.selected:
            outline, width = C_SEL_B, 4
        self._round_rect(x1, y1, x2, y2, 12, fill=fill, outline=outline, width=width)
        self.node_bbox[node] = (x1, y1, x2, y2)
        if node.is_menu():
            self.canvas.create_text(cx, cy - 8, text=node.teks, font=("", 10, "bold"),
                                    width=BW - 16, justify="center")
            self.canvas.create_text(cx, cy + 14, text=format_rupiah(node.harga),
                                    font=("", 9), fill="#a05a00")
        else:
            self.canvas.create_text(cx, cy, text=node.teks, font=("", 10),
                                    width=BW - 16, justify="center")

    def _on_click(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        for node, (x1, y1, x2, y2) in self.node_bbox.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                self.selected = node
                self.gambar_pohon()
                self._tampil_detail(node)
                return
        self.selected = None
        self.gambar_pohon()
        self._tampil_detail(None)

    # ---------- Panel kanan ----------

    def _kosongkan_panel(self):
        for w in self.panel.winfo_children():
            w.destroy()

    def _legend(self):
        for warna, teks in ((C_TANYA, "Pertanyaan"), (C_MENU, "Menu (pilihan akhir)")):
            row = ttk.Frame(self.panel)
            row.pack(anchor=tk.W, pady=1)
            tk.Label(row, text="   ", bg=warna, relief="solid", borderwidth=1).pack(side=tk.LEFT)
            ttk.Label(row, text="  " + teks).pack(side=tk.LEFT)
        ttk.Label(self.panel, text="Cabang kiri = Ya · kanan = Tidak",
                  foreground="#777").pack(anchor=tk.W, pady=(3, 0))

    def _tampil_detail(self, node):
        self._kosongkan_panel()
        ttk.Label(self.panel, text="Keterangan", font=("", 12, "bold")).pack(anchor=tk.W)
        ttk.Separator(self.panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(4, 8))
        self._legend()
        ttk.Separator(self.panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        if node is None:
            ttk.Label(self.panel, text="Klik sebuah node di pohon untuk\nmelihat detail & memilihnya.",
                      foreground="#555", justify=tk.LEFT).pack(anchor=tk.W)
            return
        jenis = "Menu" if node.is_menu() else "Pertanyaan"
        ttk.Label(self.panel, text=f"Terpilih: {jenis}", font=("", 10, "bold")).pack(anchor=tk.W)
        ttk.Label(self.panel, text=node.teks, wraplength=240, justify=tk.LEFT,
                  font=("", 11)).pack(anchor=tk.W, pady=(2, 4))
        if node.is_menu():
            ttk.Label(self.panel, text=format_rupiah(node.harga),
                      foreground="#a05a00", font=("", 11, "bold")).pack(anchor=tk.W)
            if node.deskripsi:
                ttk.Label(self.panel, text=node.deskripsi, wraplength=240,
                          justify=tk.LEFT, foreground="#555").pack(anchor=tk.W, pady=(2, 0))

    # ---------- Pandu (di layar Coba) ----------

    def _pandu_render(self, node):
        self.highlight = set(self.pandu_path) | {node}
        self.gambar_pohon()
        self._kosongkan_panel()
        ttk.Label(self.panel, text="🍽  Pandu Pesan", font=("", 13, "bold")).pack(anchor=tk.W)
        ttk.Separator(self.panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(4, 10))

        if node.is_menu():
            ttk.Label(self.panel, text="Rekomendasi untukmu:", foreground="#555").pack(anchor=tk.W)
            ttk.Label(self.panel, text=node.teks, font=("", 14, "bold"),
                      wraplength=240, justify=tk.LEFT).pack(anchor=tk.W, pady=(4, 2))
            ttk.Label(self.panel, text=format_rupiah(node.harga),
                      foreground="#a05a00", font=("", 12, "bold")).pack(anchor=tk.W)
            if node.deskripsi:
                ttk.Label(self.panel, text=node.deskripsi, wraplength=240,
                          justify=tk.LEFT, foreground="#555").pack(anchor=tk.W, pady=(6, 8))
            ttk.Button(self.panel, text="↻  Ulangi", command=self._pandu_ulang).pack(fill=tk.X, pady=3)
            ttk.Button(self.panel, text="← Beranda", command=self.tampil_beranda).pack(fill=tk.X, pady=3)
        else:
            ttk.Label(self.panel, text=node.teks, font=("", 14, "bold"),
                      wraplength=240, justify=tk.LEFT).pack(anchor=tk.W, pady=(4, 12))
            ttk.Button(self.panel, text="✓   Ya",
                       command=lambda: self._pandu_maju(node, node.ya)).pack(fill=tk.X, pady=4)
            ttk.Button(self.panel, text="✗   Tidak",
                       command=lambda: self._pandu_maju(node, node.tidak)).pack(fill=tk.X, pady=4)
            ttk.Label(self.panel, text="Jalur jawaban ter-sorot hijau di pohon →",
                      foreground="#888", wraplength=240).pack(anchor=tk.W, pady=(12, 0))

    def _pandu_maju(self, node, anak):
        self.pandu_path.append(node)
        self._pandu_render(anak)

    def _pandu_ulang(self):
        self.pandu_path = []
        self._pandu_render(self.akar)

    # ---------- Aksi kelola ----------

    def aksi_buat_menu(self):
        dialog = BuatMenuDialog(self.root_window)
        self.root_window.wait_window(dialog.top)
        if dialog.berhasil:
            self.akar = Node(dialog.nama, harga=dialog.harga, deskripsi=dialog.deskripsi)
            self._save()
            self.tampil_kelola()      # rebuild (keluar dari empty-state)

    def aksi_tambah(self):
        node = self.selected
        if node is None:
            messagebox.showinfo("Pecah jadi Pertanyaan", "Klik dulu node MENU (kuning) yang mau dipecah.")
            return
        if not node.is_menu():
            messagebox.showwarning("Pecah jadi Pertanyaan",
                                   "Hanya node MENU (kuning) yang bisa dipecah jadi pertanyaan.")
            return
        dialog = TambahDialog(self.root_window, node)
        self.root_window.wait_window(dialog.top)
        if dialog.berhasil:
            self._after_edit()

    def aksi_edit(self):
        node = self.selected
        if node is None:
            messagebox.showinfo("Edit", "Klik node yang mau diedit dulu.")
            return
        dialog = EditDialog(self.root_window, node)
        self.root_window.wait_window(dialog.top)
        if dialog.berhasil:
            self._after_edit()

    def aksi_hapus(self):
        node = self.selected
        if node is None:
            messagebox.showinfo("Hapus", "Klik node yang mau dihapus dulu.")
            return
        if node is self.akar:
            if node.is_menu():
                if messagebox.askyesno("Hapus", f"Hapus menu terakhir '{node.teks}'?\n"
                                                 "Pohon jadi kosong lagi."):
                    self.akar = None
                    self._save()
                    self.tampil_kelola()
            else:
                messagebox.showwarning("Hapus", "Akar berupa pertanyaan tidak bisa dihapus "
                                                "(hapus/Edit cabangnya saja).")
            return
        ket = f"menu '{node.teks}'" if node.is_menu() else f"pertanyaan '{node.teks}' + sub-pohonnya"
        if not messagebox.askyesno("Konfirmasi Hapus",
                                   f"Yakin hapus {ket}?\n\nPertanyaan induknya runtuh, "
                                   "cabang saudaranya naik menggantikan."):
            return
        self.akar, ok = hapus(self.akar, node)
        if ok:
            self.selected = None
            self._after_edit()

    def _after_edit(self):
        self._save()
        self.highlight = set()
        self.gambar_pohon()
        self._tampil_detail(self.selected)
        self._update_status()

    def aksi_traversal(self):
        if self.akar is None:
            return
        win = tk.Toplevel(self.root_window)
        win.title("Kunjungan (Traversal) Pohon")
        win.geometry("700x420")
        win.configure(bg="#f3f3f3")
        win.transient(self.root_window)
        frame = ttk.Frame(win, padding=8)
        frame.pack(fill=tk.BOTH, expand=True)
        text = tk.Text(frame, wrap=tk.WORD, font=("Menlo", 11),
                       background="#ffffff", foreground="#1a1a1a")
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        def baris(nodes):
            return "  →  ".join(n.teks for n in nodes)

        text.insert(tk.END, "PREORDER  (Akar → Ya → Tidak)\n" + baris(preorder(self.akar)) + "\n\n")
        text.insert(tk.END, "INORDER   (Ya → Akar → Tidak)\n" + baris(inorder(self.akar)) + "\n\n")
        text.insert(tk.END, "POSTORDER (Ya → Tidak → Akar)\n" + baris(postorder(self.akar)) + "\n")
        text.config(state=tk.DISABLED)
        ttk.Button(win, text="Tutup", command=win.destroy).pack(pady=(0, 8))

    def aksi_statistik(self):
        m, q = hitung_menu(self.akar), hitung_pertanyaan(self.akar)
        messagebox.showinfo("Statistik", "\n".join([
            f"Jumlah menu (daun) : {m}",
            f"Jumlah pertanyaan  : {q}",
            f"Total node         : {m + q}",
            f"Tinggi pohon       : {tinggi(self.akar)}",
        ]))

    def _update_status(self):
        if not hasattr(self, "status_var"):
            return
        m, q = hitung_menu(self.akar), hitung_pertanyaan(self.akar)
        self.status_var.set(f"Menu: {m}   |   Pertanyaan: {q}   |   "
                            f"Tinggi pohon: {tinggi(self.akar)}   |   File: {os.path.basename(FILE_DATA)}")

    def _save(self):
        simpan(self.akar, FILE_DATA)


def apply_light_theme(root_window):
    """Workaround macOS Dark Mode: paksa theme 'clam' + warna eksplisit."""
    root_window.configure(bg="#f3f3f3")
    style = ttk.Style(root_window)
    if "clam" in style.theme_names():
        style.theme_use("clam")
    BG, FG, PANEL = "#f3f3f3", "#1a1a1a", "#ffffff"
    BTN_BG, BTN_HV = "#e6e6e6", "#d4d4d4"
    style.configure(".", background=BG, foreground=FG)
    style.configure("TFrame", background=BG)
    style.configure("TLabel", background=BG, foreground=FG)
    style.configure("TSeparator", background="#cccccc")
    style.configure("TButton", background=BTN_BG, foreground=FG, padding=6)
    style.map("TButton", background=[("active", BTN_HV), ("pressed", BTN_HV)])
    style.configure("TEntry", fieldbackground=PANEL, foreground=FG)
    style.configure("TCombobox", fieldbackground=PANEL, foreground=FG,
                    background=PANEL, arrowcolor=FG)
    style.map("TCombobox", fieldbackground=[("readonly", PANEL)], foreground=[("readonly", FG)])
    root_window.option_add("*TCombobox*Listbox.background", PANEL)
    root_window.option_add("*TCombobox*Listbox.foreground", FG)


def cek_versi_tk(root_window):
    """Peringatan kalau Tk < 8.6 (rendering rusak di macOS baru → jendela hitam)."""
    patch = root_window.tk.call("info", "patchlevel")
    try:
        mayor, minor = (int(x) for x in patch.split(".")[:2])
    except ValueError:
        return
    if (mayor, minor) < (8, 6):
        messagebox.showwarning(
            "Versi Tk lama terdeteksi",
            f"Tcl/Tk {patch} bermasalah di macOS baru — jendela bisa tampil hitam/blank.\n\n"
            f"Jalankan dengan interpreter ber-Tk 9.0, misalnya:\n    /opt/homebrew/bin/python3 main.py",
        )


def main():
    root_window = tk.Tk()
    apply_light_theme(root_window)
    cek_versi_tk(root_window)
    App(root_window)
    root_window.update_idletasks()
    root_window.update()
    root_window.mainloop()


if __name__ == "__main__":
    main()
