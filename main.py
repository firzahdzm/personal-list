"""
main.py
GUI version (Tkinter) untuk Katalog Koleksi Pribadi.
Struktur data inti = Binary Search Tree (lihat tree.py). Tiap item koleksi
jadi satu node BST dengan key = judul. GUI menampilkan struktur kiri/kanan,
plus fitur khas binary tree: pencarian (binary search) & kunjungan
(preorder / inorder / postorder).
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from tree import (
    sisip,
    cari,
    hapus,
    preorder,
    inorder,
    postorder,
    tinggi,
    hitung,
    hitung_per_tipe,
)
from storage import simpan, muat

# Anchor ke folder script ini, bukan ke current working directory,
# supaya program tetap jalan walau di-run dari folder mana pun.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_DATA = os.path.join(BASE_DIR, "koleksi.py")

# Atribut detail per tipe (nama, fungsi konversi untuk validasi).
ATRIBUT = {
    "Musik": [("durasi", str), ("tahun", int)],
    "Film":  [("tahun", int), ("rating", float)],
    "Game":  [("rating", float), ("jam_main", int)],
    "Buku":  [("tahun", int), ("halaman", int)],
}


# =========================================================================
#  Dialog: Tambah Item
# =========================================================================

class TambahDialog:
    """Dialog modal untuk menambah item baru ke BST. Field atribut berubah
    dinamis saat tipe dipilih."""

    def __init__(self, parent, app):
        self.app = app
        self.berhasil = False

        self.top = tk.Toplevel(parent)
        self.top.title("Tambah Item")
        self.top.geometry("420x460")
        self.top.configure(bg="#f3f3f3")
        self.top.transient(parent)
        self.top.grab_set()

        # Tipe
        ttk.Label(self.top, text="Tipe:", font=("", 10, "bold")).pack(
            anchor=tk.W, padx=12, pady=(12, 0)
        )
        self.tipe_var = tk.StringVar()
        self.tipe_combo = ttk.Combobox(
            self.top, textvariable=self.tipe_var,
            values=list(ATRIBUT.keys()), state="readonly",
        )
        self.tipe_combo.pack(fill=tk.X, padx=12, pady=4)
        self.tipe_combo.bind("<<ComboboxSelected>>", self._on_tipe_changed)

        # Judul (key BST)
        ttk.Label(self.top, text="Judul (dipakai sebagai key BST):",
                  font=("", 10, "bold")).pack(anchor=tk.W, padx=12, pady=(8, 0))
        self.judul_var = tk.StringVar()
        ttk.Entry(self.top, textvariable=self.judul_var).pack(fill=tk.X, padx=12, pady=4)

        ttk.Separator(self.top, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=12, pady=8)

        # Container atribut dinamis
        self.fields_frame = ttk.Frame(self.top, padding=(12, 0))
        self.fields_frame.pack(fill=tk.BOTH, expand=True)

        # Tombol
        button_frame = ttk.Frame(self.top, padding=12)
        button_frame.pack(fill=tk.X)
        ttk.Button(button_frame, text="Batal",
                   command=self.top.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(button_frame, text="Simpan",
                   command=self._simpan).pack(side=tk.RIGHT)

        self.attr_widgets = {}   # attr_name -> (var, type_func)
        ttk.Label(self.fields_frame,
                  text="(Pilih tipe dulu untuk menampilkan atribut)",
                  foreground="gray").pack(pady=20)

    def _on_tipe_changed(self, _event=None):
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        self.attr_widgets.clear()

        tipe = self.tipe_var.get()
        if not tipe:
            return

        ttk.Label(self.fields_frame, text="Detail Item",
                  font=("", 10, "bold")).pack(anchor=tk.W)
        for attr_nama, attr_type in ATRIBUT[tipe]:
            ttk.Label(self.fields_frame,
                      text=f"{attr_nama} ({attr_type.__name__}):").pack(anchor=tk.W, pady=(4, 0))
            var = tk.StringVar()
            ttk.Entry(self.fields_frame, textvariable=var).pack(fill=tk.X)
            self.attr_widgets[attr_nama] = (var, attr_type)

    def _simpan(self):
        tipe = self.tipe_var.get()
        if not tipe:
            messagebox.showerror("Error", "Pilih tipe dulu.", parent=self.top)
            return

        judul = self.judul_var.get().strip()
        if not judul:
            messagebox.showerror("Error", "Judul tidak boleh kosong.", parent=self.top)
            return

        # Validasi & konversi atribut
        data = {}
        for attr_nama, (var, attr_type) in self.attr_widgets.items():
            raw = var.get().strip()
            if not raw:
                messagebox.showerror("Error", f"Atribut '{attr_nama}' tidak boleh kosong.",
                                     parent=self.top)
                return
            try:
                data[attr_nama] = attr_type(raw)
            except ValueError:
                messagebox.showerror(
                    "Error", f"Atribut '{attr_nama}' harus tipe {attr_type.__name__}.",
                    parent=self.top)
                return

        # Sisip ke BST (tolak duplikat judul)
        akar_baru, ok = sisip(self.app.akar, judul, tipe, data)
        if not ok:
            messagebox.showerror(
                "Error", f"Judul '{judul}' sudah ada di pohon.\nKey BST harus unik.",
                parent=self.top)
            return

        self.app.akar = akar_baru
        self.berhasil = True
        self.top.destroy()


# =========================================================================
#  Main App
# =========================================================================

class KatalogApp:
    def __init__(self, root_window):
        self.root_window = root_window
        self.root_window.title("Katalog Koleksi Pribadi — Binary Search Tree")
        self.root_window.geometry("860x580")

        # Akar BST (None kalau kosong)
        self.akar = muat(FILE_DATA)

        # iid (Treeview) -> Node
        self.iid_to_node = {}

        self._build_toolbar()
        self._build_treeview()
        self._build_statusbar()
        self.refresh()

    # ---------- UI builders ----------

    def _build_toolbar(self):
        bar = ttk.Frame(self.root_window, padding=8)
        bar.pack(fill=tk.X)

        ttk.Button(bar, text="+ Tambah",  command=self.aksi_tambah).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="− Hapus",   command=self.aksi_hapus).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Cari…",     command=self.aksi_cari).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Traversal", command=self.aksi_traversal).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="Statistik", command=self.aksi_statistik).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="↻ Refresh", command=self.refresh).pack(side=tk.LEFT, padx=2)

    def _build_treeview(self):
        frame = ttk.Frame(self.root_window, padding=(8, 0, 8, 4))
        frame.pack(fill=tk.BOTH, expand=True)

        self.tv = ttk.Treeview(frame, columns=("posisi", "tipe", "detail"))
        self.tv.heading("#0", text="Judul (struktur pohon)")
        self.tv.heading("posisi", text="Posisi")
        self.tv.heading("tipe", text="Tipe")
        self.tv.heading("detail", text="Detail")
        self.tv.column("#0", width=300, stretch=True)
        self.tv.column("posisi", width=90, stretch=False, anchor=tk.CENTER)
        self.tv.column("tipe", width=70, stretch=False, anchor=tk.CENTER)
        self.tv.column("detail", width=260, stretch=True)

        vscroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tv.yview)
        self.tv.configure(yscrollcommand=vscroll.set)

        self.tv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tv.bind("<Delete>", lambda _e: self.aksi_hapus())

    def _build_statusbar(self):
        self.status_var = tk.StringVar()
        bar = ttk.Label(self.root_window, textvariable=self.status_var,
                        padding=(8, 4), relief=tk.SUNKEN, anchor=tk.W)
        bar.pack(fill=tk.X)

    # ---------- Rendering BST ----------

    def refresh(self):
        """Render ulang Treeview dari akar BST (struktur kiri/kanan)."""
        for iid in self.tv.get_children():
            self.tv.delete(iid)
        self.iid_to_node.clear()
        if self.akar is not None:
            self._insert_node("", self.akar, "● akar")
        self._update_status()

    def _insert_node(self, parent_iid, node, posisi):
        detail = ", ".join(f"{k}: {v}" for k, v in node.data.items())
        iid = self.tv.insert(parent_iid, "end", text=node.judul,
                             values=(posisi, node.tipe, detail), open=True)
        self.iid_to_node[iid] = node
        if node.kiri is not None:
            self._insert_node(iid, node.kiri, "↙ kiri")
        if node.kanan is not None:
            self._insert_node(iid, node.kanan, "↘ kanan")

    def _update_status(self):
        total = hitung(self.akar)
        h = tinggi(self.akar)
        self.status_var.set(
            f"Total: {total} item   |   Tinggi pohon: {h}   |   "
            f"File: {os.path.basename(FILE_DATA)}"
        )

    def _save(self):
        simpan(self.akar, FILE_DATA)

    # ---------- Aksi tombol ----------

    def aksi_tambah(self):
        dialog = TambahDialog(self.root_window, self)
        self.root_window.wait_window(dialog.top)
        if dialog.berhasil:
            self._save()
            self.refresh()

    def aksi_hapus(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showinfo("Hapus", "Pilih node yang ingin dihapus dulu di pohon.")
            return
        node = self.iid_to_node[sel[0]]

        ket = "daun / 1 anak → langsung disambung"
        if node.kiri is not None and node.kanan is not None:
            ket = "punya 2 anak → diganti suksesor inorder (aturan BST)"
        konfirmasi = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Yakin hapus '{node.judul}'?\n[{ket}]",
        )
        if not konfirmasi:
            return

        self.akar, ok = hapus(self.akar, node.judul)
        if ok:
            self._save()
            self.refresh()

    def aksi_cari(self):
        judul = simpledialog.askstring(
            "Cari (binary search)", "Judul yang dicari (case-insensitive):",
            parent=self.root_window,
        )
        if not judul:
            return
        node, langkah = cari(self.akar, judul)
        if node is None:
            messagebox.showinfo(
                "Cari", f"'{judul}' tidak ditemukan.\n"
                        f"({langkah} langkah perbandingan)")
            return
        detail = ", ".join(f"{k}: {v}" for k, v in node.data.items())
        messagebox.showinfo(
            "Cari",
            f"Ditemukan!\n\n"
            f"Judul  : {node.judul}\n"
            f"Tipe   : {node.tipe}\n"
            f"Detail : {detail}\n\n"
            f"Hanya butuh {langkah} langkah perbandingan (binary search).",
        )

    def aksi_traversal(self):
        if self.akar is None:
            messagebox.showinfo("Traversal", "Pohon masih kosong.")
            return

        win = tk.Toplevel(self.root_window)
        win.title("Kunjungan (Traversal) Binary Tree")
        win.geometry("680x420")
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

        def baris(judul_judul):
            return "  →  ".join(judul_judul)

        text.insert(tk.END, "PREORDER  (Akar → Kiri → Kanan)\n")
        text.insert(tk.END, baris([n.judul for n in preorder(self.akar)]) + "\n\n")
        text.insert(tk.END, "INORDER   (Kiri → Akar → Kanan)  —  otomatis TERURUT\n")
        text.insert(tk.END, baris([n.judul for n in inorder(self.akar)]) + "\n\n")
        text.insert(tk.END, "POSTORDER (Kiri → Kanan → Akar)\n")
        text.insert(tk.END, baris([n.judul for n in postorder(self.akar)]) + "\n")
        text.config(state=tk.DISABLED)

        ttk.Button(win, text="Tutup", command=win.destroy).pack(pady=(0, 8))

    def aksi_statistik(self):
        total = hitung(self.akar)
        h = tinggi(self.akar)
        per_tipe = hitung_per_tipe(self.akar)

        baris = [
            f"Total item     : {total}",
            f"Tinggi pohon   : {h}",
            "",
        ]
        if per_tipe:
            baris.append("Per tipe:")
            for tipe, count in sorted(per_tipe.items()):
                baris.append(f"  • {tipe:6s}: {count}")
            terbanyak = max(per_tipe, key=per_tipe.get)
            baris.append("")
            baris.append(f"Tipe terbanyak : {terbanyak} ({per_tipe[terbanyak]} item)")
        else:
            baris.append("(Pohon masih kosong.)")

        messagebox.showinfo("Statistik", "\n".join(baris))


def apply_light_theme(root_window):
    """
    Workaround macOS Tcl/Tk 8.5 + Dark Mode:
    Widget ttk.* default ngikut sistem Dark Mode → semua jadi hitam-di-atas-hitam.
    Force pakai theme 'clam' + override warna semua ttk widget secara eksplisit.
    """
    root_window.configure(bg="#f3f3f3")

    style = ttk.Style(root_window)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    BG     = "#f3f3f3"
    FG     = "#1a1a1a"
    PANEL  = "#ffffff"
    SEL_BG = "#3a7afe"
    SEL_FG = "#ffffff"
    BTN_BG = "#e6e6e6"
    BTN_HV = "#d4d4d4"

    style.configure(".",          background=BG, foreground=FG)
    style.configure("TFrame",     background=BG)
    style.configure("TLabel",     background=BG, foreground=FG)
    style.configure("TSeparator", background="#cccccc")
    style.configure("TButton",    background=BTN_BG, foreground=FG, padding=6)
    style.map("TButton", background=[("active", BTN_HV), ("pressed", BTN_HV)])
    style.configure("TEntry",     fieldbackground=PANEL, foreground=FG)
    style.configure("TCombobox",  fieldbackground=PANEL, foreground=FG,
                                  background=PANEL, arrowcolor=FG)
    style.map("TCombobox",
              fieldbackground=[("readonly", PANEL)],
              foreground=[("readonly", FG)])
    style.configure("Treeview",   background=PANEL, foreground=FG,
                                  fieldbackground=PANEL, rowheight=24)
    style.configure("Treeview.Heading", background="#dddddd", foreground=FG)
    style.map("Treeview",
              background=[("selected", SEL_BG)],
              foreground=[("selected", SEL_FG)])

    root_window.option_add("*TCombobox*Listbox.background", PANEL)
    root_window.option_add("*TCombobox*Listbox.foreground", FG)
    root_window.option_add("*TCombobox*Listbox.selectBackground", SEL_BG)
    root_window.option_add("*TCombobox*Listbox.selectForeground", SEL_FG)


def main():
    root_window = tk.Tk()
    apply_light_theme(root_window)

    KatalogApp(root_window)

    root_window.update_idletasks()
    root_window.update()

    root_window.mainloop()


if __name__ == "__main__":
    main()
