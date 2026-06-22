"""
main.py
GUI Buku Telepon (Tkinter) berbasis Binary Search Tree.
Tiap kontak = satu node BST dengan key = nama. GUI menampilkan struktur
kiri/kanan, plus fitur khas binary tree: pencarian (binary search) &
kunjungan (preorder / inorder / postorder).
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
    hitung_per_kategori,
)
from storage import simpan, muat

# Anchor ke folder script ini, bukan current working directory,
# supaya program tetap jalan walau di-run dari folder mana pun.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_DATA = os.path.join(BASE_DIR, "kontak.py")

# Saran kategori (combobox bisa diketik manual juga).
KATEGORI = ["Keluarga", "Teman", "Kerja", "Sekolah", "Darurat", "Lainnya"]


# =========================================================================
#  Dialog: Tambah Kontak
# =========================================================================

class TambahDialog:
    """Dialog modal untuk menambah kontak baru ke BST."""

    def __init__(self, parent, app):
        self.app = app
        self.berhasil = False

        self.top = tk.Toplevel(parent)
        self.top.title("Tambah Kontak")
        self.top.geometry("400x300")
        self.top.configure(bg="#f3f3f3")
        self.top.transient(parent)
        self.top.grab_set()

        form = ttk.Frame(self.top, padding=12)
        form.pack(fill=tk.BOTH, expand=True)

        # Nama (key BST)
        ttk.Label(form, text="Nama (dipakai sebagai key BST):",
                  font=("", 10, "bold")).pack(anchor=tk.W, pady=(0, 0))
        self.nama_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.nama_var).pack(fill=tk.X, pady=(2, 8))

        # Nomor
        ttk.Label(form, text="Nomor telepon:",
                  font=("", 10, "bold")).pack(anchor=tk.W)
        self.nomor_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.nomor_var).pack(fill=tk.X, pady=(2, 8))

        # Kategori (boleh pilih atau ketik)
        ttk.Label(form, text="Kategori:",
                  font=("", 10, "bold")).pack(anchor=tk.W)
        self.kategori_var = tk.StringVar()
        ttk.Combobox(form, textvariable=self.kategori_var,
                     values=KATEGORI).pack(fill=tk.X, pady=(2, 8))

        # Tombol
        button_frame = ttk.Frame(self.top, padding=12)
        button_frame.pack(fill=tk.X)
        ttk.Button(button_frame, text="Batal",
                   command=self.top.destroy).pack(side=tk.RIGHT, padx=4)
        ttk.Button(button_frame, text="Simpan",
                   command=self._simpan).pack(side=tk.RIGHT)

    def _simpan(self):
        nama = self.nama_var.get().strip()
        if not nama:
            messagebox.showerror("Error", "Nama tidak boleh kosong.", parent=self.top)
            return
        nomor = self.nomor_var.get().strip()
        if not nomor:
            messagebox.showerror("Error", "Nomor tidak boleh kosong.", parent=self.top)
            return
        kategori = self.kategori_var.get().strip()

        # Sisip ke BST (tolak duplikat nama)
        akar_baru, ok = sisip(self.app.akar, nama, nomor, kategori)
        if not ok:
            messagebox.showerror(
                "Error", f"Nama '{nama}' sudah ada di buku telepon.\nKey BST harus unik.",
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
        self.root_window.title("Buku Telepon — Binary Search Tree")
        self.root_window.geometry("820x560")

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

        self.tv = ttk.Treeview(frame, columns=("posisi", "nomor", "kategori"))
        self.tv.heading("#0", text="Nama (struktur pohon)")
        self.tv.heading("posisi", text="Posisi")
        self.tv.heading("nomor", text="Nomor")
        self.tv.heading("kategori", text="Kategori")
        self.tv.column("#0", width=280, stretch=True)
        self.tv.column("posisi", width=90, stretch=False, anchor=tk.CENTER)
        self.tv.column("nomor", width=160, stretch=False, anchor=tk.CENTER)
        self.tv.column("kategori", width=110, stretch=False, anchor=tk.CENTER)

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
        iid = self.tv.insert(parent_iid, "end", text=node.nama,
                             values=(posisi, node.nomor, node.kategori), open=True)
        self.iid_to_node[iid] = node
        if node.kiri is not None:
            self._insert_node(iid, node.kiri, "↙ kiri")
        if node.kanan is not None:
            self._insert_node(iid, node.kanan, "↘ kanan")

    def _update_status(self):
        total = hitung(self.akar)
        h = tinggi(self.akar)
        self.status_var.set(
            f"Total: {total} kontak   |   Tinggi pohon: {h}   |   "
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
            messagebox.showinfo("Hapus", "Pilih kontak yang ingin dihapus dulu di pohon.")
            return
        node = self.iid_to_node[sel[0]]

        ket = "daun / 1 anak → langsung disambung"
        if node.kiri is not None and node.kanan is not None:
            ket = "punya 2 anak → diganti suksesor inorder (aturan BST)"
        konfirmasi = messagebox.askyesno(
            "Konfirmasi Hapus",
            f"Yakin hapus kontak '{node.nama}'?\n[{ket}]",
        )
        if not konfirmasi:
            return

        self.akar, ok = hapus(self.akar, node.nama)
        if ok:
            self._save()
            self.refresh()

    def aksi_cari(self):
        nama = simpledialog.askstring(
            "Cari (binary search)", "Nama yang dicari (case-insensitive):",
            parent=self.root_window,
        )
        if not nama:
            return
        node, langkah = cari(self.akar, nama)
        if node is None:
            messagebox.showinfo(
                "Cari", f"'{nama}' tidak ditemukan.\n"
                        f"({langkah} langkah perbandingan)")
            return
        messagebox.showinfo(
            "Cari",
            f"Ditemukan!\n\n"
            f"Nama     : {node.nama}\n"
            f"Nomor    : {node.nomor}\n"
            f"Kategori : {node.kategori}\n\n"
            f"Hanya butuh {langkah} langkah perbandingan (binary search).",
        )

    def aksi_traversal(self):
        if self.akar is None:
            messagebox.showinfo("Traversal", "Buku telepon masih kosong.")
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

        def baris(nama_nama):
            return "  →  ".join(nama_nama)

        text.insert(tk.END, "PREORDER  (Akar → Kiri → Kanan)\n")
        text.insert(tk.END, baris([n.nama for n in preorder(self.akar)]) + "\n\n")
        text.insert(tk.END, "INORDER   (Kiri → Akar → Kanan)  —  otomatis TERURUT A-Z\n")
        text.insert(tk.END, baris([n.nama for n in inorder(self.akar)]) + "\n\n")
        text.insert(tk.END, "POSTORDER (Kiri → Kanan → Akar)\n")
        text.insert(tk.END, baris([n.nama for n in postorder(self.akar)]) + "\n")
        text.config(state=tk.DISABLED)

        ttk.Button(win, text="Tutup", command=win.destroy).pack(pady=(0, 8))

    def aksi_statistik(self):
        total = hitung(self.akar)
        h = tinggi(self.akar)
        per_kat = hitung_per_kategori(self.akar)

        baris = [
            f"Total kontak   : {total}",
            f"Tinggi pohon   : {h}",
            "",
        ]
        if per_kat:
            baris.append("Per kategori:")
            for kat, count in sorted(per_kat.items()):
                baris.append(f"  • {kat:10s}: {count}")
            terbanyak = max(per_kat, key=per_kat.get)
            baris.append("")
            baris.append(f"Kategori terbanyak : {terbanyak} ({per_kat[terbanyak]} kontak)")
        else:
            baris.append("(Buku telepon masih kosong.)")

        messagebox.showinfo("Statistik", "\n".join(baris))


def apply_light_theme(root_window):
    """
    Workaround macOS Tcl/Tk + Dark Mode:
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


def cek_versi_tk(root_window):
    """
    Peringatan kalau Tk < 8.6. Di macOS baru, Tk 8.5 (bawaan /usr/bin/python3)
    rendering-nya rusak → jendela tampil hitam/blank. Solusinya pakai
    interpreter ber-Tk 9.0 (mis. /opt/homebrew/bin/python3).
    """
    patch = root_window.tk.call("info", "patchlevel")   # mis. "8.5.9" / "9.0.3"
    try:
        mayor, minor = (int(x) for x in patch.split(".")[:2])
    except ValueError:
        return
    if (mayor, minor) < (8, 6):
        messagebox.showwarning(
            "Versi Tk lama terdeteksi",
            f"Tcl/Tk {patch} bermasalah di macOS baru — jendela bisa "
            f"tampil hitam/blank.\n\n"
            f"Jalankan dengan interpreter ber-Tk 9.0, misalnya:\n"
            f"    /opt/homebrew/bin/python3 main.py",
        )


def main():
    root_window = tk.Tk()
    apply_light_theme(root_window)
    cek_versi_tk(root_window)

    KatalogApp(root_window)

    root_window.update_idletasks()
    root_window.update()

    root_window.mainloop()


if __name__ == "__main__":
    main()
