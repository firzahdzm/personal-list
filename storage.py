"""
storage.py
Simpan/muat BST ke file Python (koleksi.py).

Trik penting: BST disimpan sebagai list ber-urutan PREORDER. Saat dimuat,
item disisipkan kembali satu per satu dengan urutan yang sama. Karena
preorder memproses akar sebelum anak, hasil rekonstruksinya PERSIS sama
dengan bentuk pohon semula (tidak berubah/menggepeng).

Data dibaca pakai ast.literal_eval (bukan exec) supaya aman — file hanya
boleh berisi literal Python, bukan kode yang bisa dieksekusi.
"""

import ast
import os
from pprint import pformat

from tree import sisip, preorder


def to_list(akar):
    """Serialisasi BST -> list dict {judul, tipe, data} urutan preorder."""
    return [
        {"judul": n.judul, "tipe": n.tipe, "data": n.data}
        for n in preorder(akar)
    ]


def from_list(items):
    """Rebuild BST dari list (disisipkan sesuai urutan list)."""
    akar = None
    for it in items:
        akar, _ = sisip(akar, it["judul"], it.get("tipe", ""), it.get("data", {}))
    return akar


def simpan(akar, path):
    """Tulis BST ke file Python berisi `koleksi = [...]` (preorder)."""
    items = to_list(akar)
    formatted = pformat(items, indent=4, sort_dicts=False, width=100)
    with open(path, "w", encoding="utf-8") as f:
        f.write("# File auto-generated oleh Katalog Koleksi Pribadi (BST).\n")
        f.write("# Urutan list = PREORDER, jangan diacak agar bentuk pohon tetap.\n\n")
        f.write(f"koleksi = {formatted}\n")


def muat(path):
    """Muat BST dari file. Return akar Node atau None bila file tidak ada/rusak."""
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    marker = "koleksi ="
    idx = src.find(marker)
    if idx == -1:
        return None
    try:
        # .strip() penting: buang spasi/newline di depan agar literal_eval
        # tidak salah mengira ada indentasi ilegal.
        items = ast.literal_eval(src[idx + len(marker):].strip())
    except (ValueError, SyntaxError):
        return None
    return from_list(items)
