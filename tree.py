"""
tree.py
Definisi class Node dan operasi Binary Search Tree (BST) — rekursif.

Binary tree: tiap node maksimal punya 2 anak (kiri & kanan).
Binary SEARCH tree: anak kiri selalu lebih kecil, anak kanan lebih besar
dari node-nya (berdasar key = judul, case-insensitive). Sifat ini bikin
pencarian jadi O(log n) dan kunjungan inorder otomatis terurut.
"""


class Node:
    def __init__(self, judul, tipe="", data=None):
        self.judul = judul              # key BST (pembanding)
        self.tipe = tipe                # Musik / Film / Game / Buku
        self.data = data if data is not None else {}
        self.kiri = None                # subpohon kiri  (judul lebih kecil)
        self.kanan = None               # subpohon kanan (judul lebih besar)

    def __repr__(self):
        return f"Node({self.judul!r}, tipe={self.tipe!r})"


def _key(judul):
    """Normalisasi key supaya urutan tidak terganggu besar/kecil huruf."""
    return judul.strip().lower()


# ---------------------------------------------------------------- sisip
def sisip(akar, judul, tipe="", data=None):
    """
    Sisipkan node baru ke BST berdasar judul.
    Return (akar_baru, berhasil). berhasil=False kalau judul sudah ada
    (BST klasik menolak duplikat key).
    """
    if akar is None:
        return Node(judul, tipe, data), True

    k_baru, k_akar = _key(judul), _key(akar.judul)
    if k_baru == k_akar:
        return akar, False                      # duplikat → tolak
    if k_baru < k_akar:
        akar.kiri, ok = sisip(akar.kiri, judul, tipe, data)
    else:
        akar.kanan, ok = sisip(akar.kanan, judul, tipe, data)
    return akar, ok


# ---------------------------------------------------------------- cari
def cari(akar, judul, langkah=0):
    """
    Binary search: turun ke kiri/kanan mengikuti perbandingan key.
    Return (node, langkah). node=None kalau tidak ketemu.
    `langkah` = jumlah perbandingan (bukti efisiensi O(log n)).
    """
    if akar is None:
        return None, langkah
    langkah += 1
    k, ka = _key(judul), _key(akar.judul)
    if k == ka:
        return akar, langkah
    if k < ka:
        return cari(akar.kiri, judul, langkah)
    return cari(akar.kanan, judul, langkah)


# ---------------------------------------------------------------- hapus
def _node_min(akar):
    """Node dengan key terkecil di subpohon (paling kiri)."""
    while akar.kiri is not None:
        akar = akar.kiri
    return akar


def hapus(akar, judul):
    """
    Hapus node berdasar judul. Return (akar_baru, berhasil).
    Tiga kasus klasik BST:
      1. tanpa anak / satu anak  -> sambung anaknya ke parent
      2. dua anak                -> ganti dengan suksesor inorder
                                    (node terkecil di subpohon kanan)
    """
    if akar is None:
        return None, False

    k, ka = _key(judul), _key(akar.judul)
    if k < ka:
        akar.kiri, ok = hapus(akar.kiri, judul)
        return akar, ok
    if k > ka:
        akar.kanan, ok = hapus(akar.kanan, judul)
        return akar, ok

    # ketemu node-nya
    if akar.kiri is None:
        return akar.kanan, True            # 0/1 anak (kanan)
    if akar.kanan is None:
        return akar.kiri, True             # 1 anak (kiri)

    # 2 anak: salin data suksesor, lalu hapus suksesor dari subpohon kanan
    suksesor = _node_min(akar.kanan)
    akar.judul, akar.tipe, akar.data = suksesor.judul, suksesor.tipe, suksesor.data
    akar.kanan, _ = hapus(akar.kanan, suksesor.judul)
    return akar, True


# ---------------------------------------------------- kunjungan (traversal)
def preorder(akar):
    """Akar -> Kiri -> Kanan."""
    if akar is None:
        return []
    return [akar] + preorder(akar.kiri) + preorder(akar.kanan)


def inorder(akar):
    """Kiri -> Akar -> Kanan. Di BST hasilnya TERURUT menaik."""
    if akar is None:
        return []
    return inorder(akar.kiri) + [akar] + inorder(akar.kanan)


def postorder(akar):
    """Kiri -> Kanan -> Akar."""
    if akar is None:
        return []
    return postorder(akar.kiri) + postorder(akar.kanan) + [akar]


# ---------------------------------------------------------------- statistik
def tinggi(akar):
    """Tinggi pohon. Kosong = 0, satu node = 1."""
    if akar is None:
        return 0
    return 1 + max(tinggi(akar.kiri), tinggi(akar.kanan))


def hitung(akar):
    """Jumlah total node."""
    if akar is None:
        return 0
    return 1 + hitung(akar.kiri) + hitung(akar.kanan)


def hitung_per_tipe(akar):
    """Return dict {tipe: jumlah}."""
    hasil = {}
    for node in preorder(akar):
        hasil[node.tipe] = hasil.get(node.tipe, 0) + 1
    return hasil
