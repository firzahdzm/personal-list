"""
tree.py
Definisi class Node dan operasi-operasi tree (rekursif).
N-ary tree: tiap node bisa punya banyak anak (children).
"""


class Node:
    def __init__(self, nama, data=None):
        self.nama = nama
        self.children = []
        self.data = data if data else {}

    def __repr__(self):
        return f"Node({self.nama!r}, anak={len(self.children)})"


def cari_anak(node, nama):
    """Cari anak langsung berdasarkan nama (case-insensitive). Return Node atau None."""
    for child in node.children:
        if child.nama.lower() == nama.lower():
            return child
    return None


def cari_rekursif(node, keyword, path=None):
    """
    DFS rekursif: cari semua node yang nama-nya mengandung keyword (case-insensitive).
    Return list of (path, node).
    """
    if path is None:
        path = []
    hasil = []
    current_path = path + [node.nama]
    if keyword.lower() in node.nama.lower() and path:
        hasil.append((current_path, node))
    for child in node.children:
        hasil.extend(cari_rekursif(child, keyword, current_path))
    return hasil


def cari_untuk_hapus(node, target_nama, path=None):
    """
    Cari semua node dengan nama cocok (case-insensitive), kembalikan beserta parent-nya
    agar bisa di-detach. Return list of (path, node, parent).
    """
    if path is None:
        path = []
    hasil = []
    current_path = path + [node.nama]
    for child in node.children:
        child_path = current_path + [child.nama]
        if child.nama.lower() == target_nama.lower():
            hasil.append((child_path, child, node))
        hasil.extend(cari_untuk_hapus(child, target_nama, current_path))
    return hasil


def tampilkan_tree(node, prefix="", is_last=True, is_root=True):
    """Pretty-print tree dengan karakter └── ├── │ untuk visualisasi."""
    if is_root:
        print(node.nama)
    else:
        connector = "└── " if is_last else "├── "
        atribut = ""
        if node.data:
            atribut_str = ", ".join(f"{k}: {v}" for k, v in node.data.items())
            atribut = f"   {{{atribut_str}}}"
        print(f"{prefix}{connector}{node.nama}{atribut}")

    if not is_root:
        prefix += "    " if is_last else "│   "

    n = len(node.children)
    for i, child in enumerate(node.children):
        last = (i == n - 1)
        tampilkan_tree(child, prefix, last, is_root=False)


def hitung_item(node):
    """Hitung total leaf node yang punya data (= item, bukan kategori kosong)."""
    if not node.children:
        return 1 if node.data else 0
    total = 0
    for child in node.children:
        total += hitung_item(child)
    return total


def kedalaman_max(node):
    """Kedalaman maksimum tree (root = 0)."""
    if not node.children:
        return 0
    return 1 + max(kedalaman_max(c) for c in node.children)


def hitung_per_tipe(root):
    """Return dict {nama_tipe: jumlah_item}. Root.children = tipe-tipe (Musik, Film, dll)."""
    hasil = {}
    for tipe_node in root.children:
        hasil[tipe_node.nama] = hitung_item(tipe_node)
    return hasil
