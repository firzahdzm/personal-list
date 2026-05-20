"""
storage.py
Konversi tree ke/dari dict, dan simpan/muat ke file Python (koleksi.py).
Format file: berisi variabel `koleksi = {...}` (dict literal Python).
"""

import os
from pprint import pformat

from tree import Node


def to_dict(node):
    """Konversi Node (beserta semua keturunannya) jadi nested dict."""
    return {
        "nama": node.nama,
        "data": node.data,
        "children": [to_dict(c) for c in node.children],
    }


def from_dict(d):
    """Rebuild tree dari nested dict. Mengembalikan root Node."""
    node = Node(d["nama"], d.get("data", {}))
    for child_dict in d.get("children", []):
        node.children.append(from_dict(child_dict))
    return node


def simpan(root, path):
    """Tulis tree ke file Python berisi dict literal."""
    data = to_dict(root)
    formatted = pformat(data, indent=4, sort_dicts=False, width=100)
    with open(path, "w", encoding="utf-8") as f:
        f.write("# File auto-generated oleh Katalog Koleksi Pribadi.\n")
        f.write("# Jangan diedit manual kecuali tahu apa yang dilakukan.\n\n")
        f.write(f"koleksi = {formatted}\n")


def muat(path):
    """Muat tree dari file Python. Return root Node atau None jika file tidak ada."""
    if not os.path.exists(path):
        return None
    namespace = {}
    with open(path, "r", encoding="utf-8") as f:
        exec(f.read(), namespace)
    if "koleksi" not in namespace:
        return None
    return from_dict(namespace["koleksi"])
