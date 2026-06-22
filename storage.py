"""
storage.py
Simpan/muat pohon keputusan ke file Python (menu.py).

Beda dengan BST, bentuk pohon keputusan ditentukan manual (bukan dari
urutan key), jadi disimpan sebagai NESTED DICT yang merekam ya/tidak tiap
node secara eksplisit.

Data dibaca pakai ast.literal_eval (bukan exec) supaya aman — file hanya
boleh berisi literal Python.
"""

import ast
import os
from pprint import pformat

from tree import Node


def to_dict(node):
    """Konversi Node (beserta keturunannya) jadi nested dict."""
    if node is None:
        return None
    return {
        "teks": node.teks,
        "harga": node.harga,
        "deskripsi": node.deskripsi,
        "ya": to_dict(node.ya),
        "tidak": to_dict(node.tidak),
    }


def from_dict(d):
    """Rebuild pohon dari nested dict. Return root Node atau None."""
    if d is None:
        return None
    node = Node(d["teks"], harga=d.get("harga"), deskripsi=d.get("deskripsi", ""))
    node.ya = from_dict(d.get("ya"))
    node.tidak = from_dict(d.get("tidak"))
    return node


def simpan(akar, path):
    """Tulis pohon ke file Python berisi `menu = {...}`."""
    data = to_dict(akar)
    formatted = pformat(data, indent=4, sort_dicts=False, width=100)
    with open(path, "w", encoding="utf-8") as f:
        f.write("# File auto-generated oleh Pemandu Pesan Menu (pohon keputusan).\n")
        f.write("# Struktur pohon biner: tiap node punya cabang 'ya' & 'tidak'.\n\n")
        f.write(f"menu = {formatted}\n")


def muat(path):
    """Muat pohon dari file. Return root Node atau None bila tidak ada/rusak."""
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()

    marker = "menu ="
    idx = src.find(marker)
    if idx == -1:
        return None
    try:
        # .strip() penting: buang spasi/newline di depan agar literal_eval
        # tidak salah mengira ada indentasi ilegal.
        data = ast.literal_eval(src[idx + len(marker):].strip())
    except (ValueError, SyntaxError):
        return None
    return from_dict(data)
