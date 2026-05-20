"""
main.py
GUI version (Tkinter) untuk Katalog Koleksi Pribadi.
Logic tree & storage di-reuse dari modul tree.py dan storage.py.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from tree import (
    Node,
    cari_anak,
    cari_rekursif,
    hitung_item,
    kedalaman_max,
    hitung_per_tipe,
)
from storage import simpan, muat

FILE_DATA = "smt-02/310--struktur-data/tugas-akhir-gui/koleksi.py"

HIERARKI = {
    "Musik": ["Genre", "Artis", "Lagu"],
    "Film":  ["Genre", "Film"],
    "Game":  ["Platform", "Genre", "Game"],
    "Buku":  ["Genre", "Buku"],
}

ATRIBUT = {
    "Musik": [("durasi", str), ("tahun", int)],
    "Film":  [("tahun", int), ("rating", float)],
    "Game":  [("rating", float), ("jam_main", int)],
    "Buku":  [("tahun", int), ("halaman", int)],
}

PILIHAN = {
    "Musik": {
        "Genre": [
            "Pop", "Rock", "Jazz", "Hip-Hop / Rap", "R&B / Soul",
            "EDM / Electronic", "Indie", "K-Pop", "Dangdut", "Klasik",
        ],
    },
    "Film": {
        "Genre": [
            "Action", "Drama", "Comedy", "Horror", "Sci-Fi",
            "Thriller", "Romance", "Animation", "Fantasy", "Documentary",
        ],
    },
    "Game": {
        "Platform": [
            "PC", "PlayStation", "Xbox", "Nintendo Switch",
            "Mobile (Android/iOS)", "Web Browser", "Handheld",
        ],
        "Genre": [
            "Action", "Adventure", "RPG", "FPS / Shooter", "Strategy",
            "Sports", "Racing", "Puzzle", "Simulation", "MOBA",
        ],
    },
    "Buku": {
        "Genre": [
            "Fiksi", "Non-Fiksi", "Novel", "Biografi", "Sejarah",
            "Self-Help", "Sains", "Komik / Manga", "Religi", "Sastra",
        ],
    },
}


# =========================================================================
#  Dialog: Tambah Item
# =========================================================================

class TambahDialog:
    """Dialog modal untuk menambahkan item baru. Fields berubah dinamis
    saat tipe dipilih."""

    def __init__(self, parent, tree_root):
        self.tree_root = tree_root
        self.berhasil = False

        self.top = tk.Toplevel(parent)
        self.top.title("Tambah Item")
        self.top.geometry("420x520")
        self.top.configure(bg="#f3f3f3")
        self.top.transient(parent)
        self.top.grab_set()

        # Tipe selector
        ttk.Label(self.top, text="Tipe:", font=("", 10, "bold")).pack(
            anchor=tk.W, padx=12, pady=(12, 0)
        )
        self.tipe_var = tk.StringVar()
        self.tipe_combo = ttk.Combobox(
            self.top,
            textvariable=self.tipe_var,
            values=list(HIERARKI.keys()),
            state="readonly",
        )
        self.tipe_combo.pack(fill=tk.X, padx=12, pady=4)
        self.tipe_combo.bind("<<ComboboxSelected>>", self._on_tipe_changed)

        # Separator
        ttk.Separator(self.top, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=12, pady=8)

        # Container untuk dynamic fields
        self.fields_frame = ttk.Frame(self.top, padding=(12, 0))
        self.fields_frame.pack(fill=tk.BOTH, expand=True)

        # Buttons
        button_frame = ttk.Frame(self.top, padding=12)
        button_frame.pack(fill=tk.X)
        ttk.Button(button_frame, text="Batal",
                   command=self.top.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(button_frame, text="Simpan",
                   command=self._simpan).pack(side=tk.RIGHT)

        # Storage state
        self.field_widgets = {}   # label → (var, custom_entry_or_None)
        self.attr_widgets = {}    # attr_name → (var, type_func)

        ttk.Label(self.fields_frame,
                  text="(Pilih tipe dulu untuk menampilkan form)",
                  foreground="gray").pack(pady=20)

    def _on_tipe_changed(self, _event=None):
        # Bersihkan fields lama
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        self.field_widgets.clear()
        self.attr_widgets.clear()

        tipe = self.tipe_var.get()
        if not tipe:
            return

        levels = HIERARKI[tipe]
        for label in levels:
            self._build_level_field(label, tipe)

        # Section detail (atribut item)
        ttk.Separator(self.fields_frame, orient=tk.HORIZONTAL).pack(
            fill=tk.X, pady=(8, 4)
        )
        ttk.Label(self.fields_frame, text="Detail Item",
                  font=("", 10, "bold")).pack(anchor=tk.W)

        for attr_nama, attr_type in ATRIBUT[tipe]:
            ttk.Label(self.fields_frame,
                      text=f"{attr_nama} ({attr_type.__name__}):").pack(anchor=tk.W, pady=(4, 0))
            var = tk.StringVar()
            ttk.Entry(self.fields_frame, textvariable=var).pack(fill=tk.X)
            self.attr_widgets[attr_nama] = (var, attr_type)

    def _build_level_field(self, label, tipe):
        ttk.Label(self.fields_frame, text=f"{label}:").pack(anchor=tk.W, pady=(4, 0))

        # Kalau level ini punya pilihan predefined → Combobox + opsi Lainnya
        if tipe in PILIHAN and label in PILIHAN[tipe]:
            var = tk.StringVar()
            values = list(PILIHAN[tipe][label]) + ["Lainnya..."]
            combo = ttk.Combobox(
                self.fields_frame, textvariable=var,
                values=values, state="readonly",
            )
            combo.pack(fill=tk.X)
            custom = ttk.Entry(self.fields_frame, state="disabled")
            custom.pack(fill=tk.X, pady=(2, 0))

            def _toggle_custom(_e, v=var, c=custom):
                if v.get() == "Lainnya...":
                    c.config(state="normal")
                    c.focus_set()
                else:
                    c.delete(0, tk.END)
                    c.config(state="disabled")

            combo.bind("<<ComboboxSelected>>", _toggle_custom)
            self.field_widgets[label] = (var, custom)
        else:
            var = tk.StringVar()
            ttk.Entry(self.fields_frame, textvariable=var).pack(fill=tk.X)
            self.field_widgets[label] = (var, None)

    def _simpan(self):
        tipe = self.tipe_var.get()
        if not tipe:
            messagebox.showerror("Error", "Pilih tipe dulu.", parent=self.top)
            return

        # Ambil nilai tiap level
        nilai_levels = []
        for label in HIERARKI[tipe]:
            var, custom = self.field_widgets[label]
            if custom is not None and var.get() == "Lainnya...":
                nilai = custom.get().strip()
            else:
                nilai = var.get().strip()
            if not nilai:
                messagebox.showerror("Error", f"{label} tidak boleh kosong.",
                                     parent=self.top)
                return
            nilai_levels.append(nilai)

        # Validasi & ambil atribut
        data = {}
        for attr_nama, (var, attr_type) in self.attr_widgets.items():
            raw = var.get().strip()
            if not raw:
                messagebox.showerror("Error",
                                     f"Atribut '{attr_nama}' tidak boleh kosong.",
                                     parent=self.top)
                return
            try:
                data[attr_nama] = attr_type(raw)
            except ValueError:
                messagebox.showerror(
                    "Error",
                    f"Atribut '{attr_nama}' harus tipe {attr_type.__name__}.",
                    parent=self.top,
                )
                return

        # Sisipkan ke tree (buat node tipe kalau belum ada)
        node_tipe = cari_anak(self.tree_root, tipe)
        if node_tipe is None:
            node_tipe = Node(tipe)
            self.tree_root.children.append(node_tipe)

        current = node_tipe
        for i, nilai in enumerate(nilai_levels):
            is_leaf = (i == len(nilai_levels) - 1)
            existing = cari_anak(current, nilai)
            if is_leaf:
                if existing:
                    messagebox.showerror(
                        "Error",
                        f"Item '{nilai}' sudah ada di lokasi yang sama.",
                        parent=self.top,
                    )
                    return
                current.children.append(Node(nilai, data))
            else:
                if existing is None:
                    existing = Node(nilai)
                    current.children.append(existing)
                current = existing

        self.berhasil = True
        self.top.destroy()


# =========================================================================
#  Main App
# =========================================================================

class KatalogApp:
    def __init__(self, root_window):
        self.root_window = root_window
        self.root_window.title("Katalog Koleksi Pribadi — N-ary Tree")
        self.root_window.geometry("820x560")

        # Load atau buat root tree
        loaded = muat(FILE_DATA)
        if loaded is None:
            self.tree_root = Node("Koleksi Pribadi")
        else:
            self.tree_root = loaded

        # iid (Treeview) → Node (object)
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
        ttk.Button(bar, text="Statistik", command=self.aksi_statistik).pack(side=tk.LEFT, padx=2)
        ttk.Button(bar, text="↻ Refresh", command=self.refresh).pack(side=tk.LEFT, padx=2)

    def _build_treeview(self):
        frame = ttk.Frame(self.root_window, padding=(8, 0, 8, 4))
        frame.pack(fill=tk.BOTH, expand=True)

        self.tv = ttk.Treeview(frame, columns=("detail",))
        self.tv.heading("#0", text="Nama")
        self.tv.heading("detail", text="Detail")
        self.tv.column("#0", width=420, stretch=True)
        self.tv.column("detail", width=320, stretch=True)

        vscroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tv.yview)
        self.tv.configure(yscrollcommand=vscroll.set)

        self.tv.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Double-click → expand/collapse otomatis (default Tkinter)
        # Delete key shortcut
        self.tv.bind("<Delete>", lambda _e: self.aksi_hapus())

    def _build_statusbar(self):
        self.status_var = tk.StringVar()
        bar = ttk.Label(self.root_window, textvariable=self.status_var,
                        padding=(8, 4), relief=tk.SUNKEN, anchor=tk.W)
        bar.pack(fill=tk.X)

    # ---------- Rendering tree ----------

    def refresh(self):
        """Render ulang Treeview dari self.tree_root."""
        for iid in self.tv.get_children():
            self.tv.delete(iid)
        self.iid_to_node.clear()
        self._insert_node("", self.tree_root)
        self._update_status()

    def _insert_node(self, parent_iid, node):
        detail = ""
        if node.data:
            detail = ", ".join(f"{k}: {v}" for k, v in node.data.items())
        iid = self.tv.insert(parent_iid, "end", text=node.nama,
                             values=(detail,), open=True)
        self.iid_to_node[iid] = node
        for child in node.children:
            self._insert_node(iid, child)

    def _update_status(self):
        total = hitung_item(self.tree_root)
        depth = kedalaman_max(self.tree_root)
        self.status_var.set(
            f"Total: {total} item   |   Kedalaman tree: {depth}   |   "
            f"File: {os.path.basename(FILE_DATA)}"
        )

    def _save(self):
        simpan(self.tree_root, FILE_DATA)

    # ---------- Aksi tombol ----------

    def aksi_tambah(self):
        dialog = TambahDialog(self.root_window, self.tree_root)
        self.root_window.wait_window(dialog.top)
        if dialog.berhasil:
            self._save()
            self.refresh()

    def aksi_hapus(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showinfo("Hapus", "Pilih node yang ingin dihapus dulu di tree.")
            return
        iid = sel[0]
        node = self.iid_to_node[iid]
        if node is self.tree_root:
            messagebox.showwarning("Hapus", "Root tidak bisa dihapus.")
            return

        parent_iid = self.tv.parent(iid)
        parent_node = self.iid_to_node[parent_iid]

        if node.data:
            keterangan = "item"
        else:
            keterangan = f"kategori (berisi {len(node.children)} anak)"

        konfirmasi = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Yakin hapus '{node.nama}'?\n[{keterangan}]\n\n"
            "Semua keturunannya juga akan ikut terhapus.",
        )
        if not konfirmasi:
            return

        parent_node.children.remove(node)
        self._save()
        self.refresh()

    def aksi_cari(self):
        keyword = simpledialog.askstring(
            "Cari", "Kata kunci (case-insensitive, partial match):",
            parent=self.root_window,
        )
        if not keyword:
            return
        hasil = cari_rekursif(self.tree_root, keyword)
        if not hasil:
            messagebox.showinfo("Cari", f"Tidak ada hasil untuk '{keyword}'.")
            return
        self._show_hasil_cari(keyword, hasil)

    def _show_hasil_cari(self, keyword, hasil):
        win = tk.Toplevel(self.root_window)
        win.title(f"Hasil pencarian: '{keyword}'")
        win.geometry("640x340")
        win.configure(bg="#f3f3f3")
        win.transient(self.root_window)

        ttk.Label(win,
                  text=f"Ditemukan {len(hasil)} hasil:",
                  padding=8, font=("", 10, "bold")).pack(anchor=tk.W)

        frame = ttk.Frame(win, padding=(8, 0, 8, 8))
        frame.pack(fill=tk.BOTH, expand=True)
        text = tk.Text(frame, wrap=tk.WORD, font=("Menlo", 10),
                       background="#ffffff", foreground="#1a1a1a",
                       insertbackground="#1a1a1a")
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=scroll.set)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        for path, node in hasil:
            atribut = ""
            if node.data:
                atribut_str = ", ".join(f"{k}: {v}" for k, v in node.data.items())
                atribut = f"   {{{atribut_str}}}"
            text.insert(tk.END, f"• {' > '.join(path)}{atribut}\n\n")
        text.config(state=tk.DISABLED)

        ttk.Button(win, text="Tutup", command=win.destroy).pack(pady=(0, 8))

    def aksi_statistik(self):
        total = hitung_item(self.tree_root)
        depth = kedalaman_max(self.tree_root)
        per_tipe = hitung_per_tipe(self.tree_root)

        baris = [
            f"Total item        : {total}",
            f"Kedalaman tree    : {depth}",
            "",
        ]
        if per_tipe:
            baris.append("Per tipe:")
            for tipe, count in per_tipe.items():
                baris.append(f"  • {tipe:6s}: {count}")
            terbanyak = max(per_tipe, key=per_tipe.get)
            if per_tipe[terbanyak] > 0:
                baris.append("")
                baris.append(f"Tipe terbanyak    : {terbanyak} ({per_tipe[terbanyak]} item)")
        else:
            baris.append("(Belum ada kategori.)")

        messagebox.showinfo("Statistik", "\n".join(baris))


def apply_light_theme(root_window):
    """
    Workaround macOS Tcl/Tk 8.5 + Dark Mode:
    Widget ttk.* default ngikut sistem Dark Mode → semua jadi hitam-di-atas-hitam.
    Force pakai theme 'clam' + override warna semua ttk widget secara eksplisit.
    """
    root_window.configure(bg="#f3f3f3")

    style = ttk.Style(root_window)
    # Theme 'clam' platform-independent, tidak ngikut Dark Mode macOS
    if "clam" in style.theme_names():
        style.theme_use("clam")

    BG       = "#f3f3f3"   # background utama
    FG       = "#1a1a1a"   # foreground (teks) utama
    PANEL    = "#ffffff"   # background panel/treeview/entry
    SEL_BG   = "#3a7afe"   # warna highlight saat dipilih
    SEL_FG   = "#ffffff"
    BTN_BG   = "#e6e6e6"
    BTN_HV   = "#d4d4d4"

    style.configure(".",            background=BG, foreground=FG)
    style.configure("TFrame",       background=BG)
    style.configure("TLabel",       background=BG, foreground=FG)
    style.configure("TSeparator",   background="#cccccc")
    style.configure("TButton",      background=BTN_BG, foreground=FG, padding=6)
    style.map("TButton",
              background=[("active", BTN_HV), ("pressed", BTN_HV)])
    style.configure("TEntry",       fieldbackground=PANEL, foreground=FG)
    style.configure("TCombobox",    fieldbackground=PANEL, foreground=FG,
                                    background=PANEL, arrowcolor=FG)
    style.map("TCombobox",
              fieldbackground=[("readonly", PANEL)],
              foreground=[("readonly", FG)])
    style.configure("Treeview",     background=PANEL, foreground=FG,
                                    fieldbackground=PANEL, rowheight=24)
    style.configure("Treeview.Heading",
                                    background="#dddddd", foreground=FG)
    style.map("Treeview",
              background=[("selected", SEL_BG)],
              foreground=[("selected", SEL_FG)])

    # Dropdown listbox-nya Combobox masih dirender pakai tk option DB —
    # set via option_add (bukan ttk.Style).
    root_window.option_add("*TCombobox*Listbox.background", PANEL)
    root_window.option_add("*TCombobox*Listbox.foreground", FG)
    root_window.option_add("*TCombobox*Listbox.selectBackground", SEL_BG)
    root_window.option_add("*TCombobox*Listbox.selectForeground", SEL_FG)


def main():
    root_window = tk.Tk()
    apply_light_theme(root_window)

    KatalogApp(root_window)

    # Force render setelah widget dibangun — fix sebagian rendering bug Tk 8.5
    root_window.update_idletasks()
    root_window.update()

    root_window.mainloop()


if __name__ == "__main__":
    main()
