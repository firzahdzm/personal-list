"""
tree.py
Definisi class Node dan operasi Binary Search Tree (BST) — rekursif.
Domain: Buku Telepon. Tiap node = 1 kontak, key = nama.

Binary tree: tiap node maksimal punya 2 anak (kiri & kanan).
Binary SEARCH tree: anak kiri selalu lebih kecil, anak kanan lebih besar
dari node-nya (berdasar key = nama, case-insensitive). Sifat ini bikin
pencarian jadi O(log n) dan kunjungan inorder otomatis terurut A-Z.
"""


class Node:
    def __init__(self, nama, nomor="", kategori=""):
        self.nama = nama                # key BST (pembanding)
        self.nomor = nomor              # nomor telepon
        self.kategori = kategori        # Keluarga / Teman / Kerja / dll
        self.kiri = None                # subpohon kiri  (nama lebih kecil)
        self.kanan = None               # subpohon kanan (nama lebih besar)

    def __repr__(self):
        return f"Node({self.nama!r}, {self.nomor!r})"


def _key(nama):
    """Normalisasi key supaya urutan tidak terganggu besar/kecil huruf."""
    return nama.strip().lower()


# ---------------------------------------------------------------- sisip
def sisip(akar, nama, nomor="", kategori=""):
    """
    Sisipkan kontak baru ke BST berdasar nama.
    Return (akar_baru, berhasil). berhasil=False kalau nama sudah ada
    (BST klasik menolak duplikat key).
    """
    if akar is None:
        return Node(nama, nomor, kategori), True

    k_baru, k_akar = _key(nama), _key(akar.nama)
    if k_baru == k_akar:
        return akar, False                      # duplikat → tolak
    if k_baru < k_akar:
        akar.kiri, ok = sisip(akar.kiri, nama, nomor, kategori)
    else:
        akar.kanan, ok = sisip(akar.kanan, nama, nomor, kategori)
    return akar, ok


# ---------------------------------------------------------------- cari
def cari(akar, nama, langkah=0):
    """
    Binary search: turun ke kiri/kanan mengikuti perbandingan key.
    Return (node, langkah). node=None kalau tidak ketemu.
    `langkah` = jumlah perbandingan (bukti efisiensi O(log n)).
    """
    if akar is None:
        return None, langkah
    langkah += 1
    k, ka = _key(nama), _key(akar.nama)
    if k == ka:
        return akar, langkah
    if k < ka:
        return cari(akar.kiri, nama, langkah)
    return cari(akar.kanan, nama, langkah)


# ---------------------------------------------------------------- hapus
def _node_min(akar):
    """Node dengan key terkecil di subpohon (paling kiri)."""
    while akar.kiri is not None:
        akar = akar.kiri
    return akar


def hapus(akar, nama):
    """
    Hapus kontak berdasar nama. Return (akar_baru, berhasil).
    Tiga kasus klasik BST:
      1. tanpa anak / satu anak  -> sambung anaknya ke parent
      2. dua anak                -> ganti dengan suksesor inorder
                                    (node terkecil di subpohon kanan)
    """
    if akar is None:
        return None, False

    k, ka = _key(nama), _key(akar.nama)
    if k < ka:
        akar.kiri, ok = hapus(akar.kiri, nama)
        return akar, ok
    if k > ka:
        akar.kanan, ok = hapus(akar.kanan, nama)
        return akar, ok

    # ketemu node-nya
    if akar.kiri is None:
        return akar.kanan, True            # 0/1 anak (kanan)
    if akar.kanan is None:
        return akar.kiri, True             # 1 anak (kiri)

    # 2 anak: salin data suksesor, lalu hapus suksesor dari subpohon kanan
    suksesor = _node_min(akar.kanan)
    akar.nama, akar.nomor, akar.kategori = suksesor.nama, suksesor.nomor, suksesor.kategori
    akar.kanan, _ = hapus(akar.kanan, suksesor.nama)
    return akar, True


# ---------------------------------------------------- kunjungan (traversal)
def preorder(akar):
    """Akar -> Kiri -> Kanan."""
    if akar is None:
        return []
    return [akar] + preorder(akar.kiri) + preorder(akar.kanan)


def inorder(akar):
    """Kiri -> Akar -> Kanan. Di BST hasilnya TERURUT A-Z."""
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
    """Jumlah total node (kontak)."""
    if akar is None:
        return 0
    return 1 + hitung(akar.kiri) + hitung(akar.kanan)


def hitung_per_kategori(akar):
    """Return dict {kategori: jumlah}."""
    hasil = {}
    for node in preorder(akar):
        kat = node.kategori or "(tanpa kategori)"
        hasil[kat] = hasil.get(kat, 0) + 1
    return hasil
