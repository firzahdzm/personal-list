"""
tree.py
Definisi class Node dan operasi Pohon Keputusan (binary decision tree).

Pohon biner: tiap node maksimal 2 anak.
Domain: pemandu pesan menu restoran.
  - Node PERTANYAAN  -> punya 2 anak: `ya` (kiri) dan `tidak` (kanan).
  - Node MENU (daun) -> tidak punya anak; menyimpan nama, harga, deskripsi.

Pelanggan menjawab ya/tidak menelusuri pohon sampai ketemu daun (menu).
"""


class Node:
    def __init__(self, teks, ya=None, tidak=None, harga=None, deskripsi=""):
        self.teks = teks            # pertanyaan (internal) / nama menu (daun)
        self.ya = ya                # anak kiri  (jawaban "ya")
        self.tidak = tidak          # anak kanan (jawaban "tidak")
        self.harga = harga          # hanya untuk daun/menu (int); None utk pertanyaan
        self.deskripsi = deskripsi  # hanya untuk daun/menu

    def is_menu(self):
        """Daun = tidak punya anak = node menu."""
        return self.ya is None and self.tidak is None

    def __repr__(self):
        jenis = "Menu" if self.is_menu() else "Tanya"
        return f"Node({jenis}: {self.teks!r})"


# ----------------------------------------------------------- edit struktur
def jadikan_pertanyaan(node, pertanyaan, menu_ya, menu_tidak):
    """
    Ubah sebuah node MENU (daun) jadi node PERTANYAAN dengan 2 daun menu baru.
    Inilah cara pohon keputusan "tumbuh": satu pilihan dipecah jadi 2.
    `menu_ya` & `menu_tidak` adalah Node menu.
    """
    node.teks = pertanyaan
    node.harga = None
    node.deskripsi = ""
    node.ya = menu_ya
    node.tidak = menu_tidak


def hapus(akar, target):
    """
    Hapus node `target` (berdasar identitas). Return (akar_baru, berhasil).

    Kalau target adalah anak sebuah pertanyaan, pertanyaan itu ikut runtuh
    dan SAUDARA target naik menggantikannya (analog hapus 1-anak di BST).
    Root tidak bisa dihapus lewat fungsi ini.
    """
    if akar is target:
        return akar, False
    return _hapus(akar, target)


def _hapus(node, target):
    if node is None or node.is_menu():
        return node, False
    if node.ya is target:
        return node.tidak, True        # runtuh: saudara "tidak" naik
    if node.tidak is target:
        return node.ya, True           # runtuh: saudara "ya" naik
    baru, ok = _hapus(node.ya, target)
    if ok:
        node.ya = baru
        return node, True
    baru, ok = _hapus(node.tidak, target)
    if ok:
        node.tidak = baru
        return node, True
    return node, False


# ----------------------------------------------------- kunjungan (traversal)
def preorder(node):
    """Akar -> Kiri(ya) -> Kanan(tidak)."""
    if node is None:
        return []
    return [node] + preorder(node.ya) + preorder(node.tidak)


def inorder(node):
    """Kiri(ya) -> Akar -> Kanan(tidak)."""
    if node is None:
        return []
    return inorder(node.ya) + [node] + inorder(node.tidak)


def postorder(node):
    """Kiri(ya) -> Kanan(tidak) -> Akar."""
    if node is None:
        return []
    return postorder(node.ya) + postorder(node.tidak) + [node]


# ---------------------------------------------------------------- statistik
def tinggi(node):
    """Tinggi pohon. Kosong = 0, satu node = 1."""
    if node is None:
        return 0
    return 1 + max(tinggi(node.ya), tinggi(node.tidak))


def hitung_menu(node):
    """Jumlah daun (menu)."""
    if node is None:
        return 0
    if node.is_menu():
        return 1
    return hitung_menu(node.ya) + hitung_menu(node.tidak)


def hitung_pertanyaan(node):
    """Jumlah node internal (pertanyaan)."""
    if node is None or node.is_menu():
        return 0
    return 1 + hitung_pertanyaan(node.ya) + hitung_pertanyaan(node.tidak)
