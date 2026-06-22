"""
storage.py
Simpan/muat BST kontak ke file Python (kontak.py).

Trik penting: BST disimpan sebagai list ber-urutan PREORDER. Saat dimuat,
kontak disisipkan kembali satu per satu dengan urutan yang sama. Karena
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
    """Serialisasi BST -> list dict {nama, nomor, kategori} urutan preorder."""
    return [
        {"nama": n.nama, "nomor": n.nomor, "kategori": n.kategori}
        for n in preorder(akar)
    ]


def from_list(items):
    """Rebuild BST dari list (disisipkan sesuai urutan list)."""
    akar = None
    for it in items:
        akar, _ = sisip(akar, it["nama"], it.get("nomor", ""), it.get("kategori", ""))
    return akar


def simpan(akar, path):
    """Tulis BST ke file Python berisi `kontak = [...]` (preorder)."""
    items = to_list(akar)
    formatted = pformat(items, indent=4, sort_dicts=False, width=100)
    with open(path, "w", encoding="utf-8") as f:
        f.write("# File auto-generated oleh Buku Telepon (BST).\n")
        f.write("# Urutan list = PREORDER, jangan diacak agar bentuk pohon tetap.\n\n")
        f.write(f"kontak = {formatted}\n")


def muat(path):
    """Muat BST dari file. Return akar Node atau None bila file tidak ada/rusak."""
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    marker = "kontak ="
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
