# File auto-generated oleh Pemandu Pesan Menu (pohon keputusan).
# Struktur pohon biner: tiap node punya cabang 'ya' & 'tidak'.
# Node pertanyaan -> harga None, punya anak. Node menu (daun) -> harga terisi,
# ya/tidak None.

menu = {
    "teks": "Mau makanan berat?",
    "harga": None,
    "deskripsi": "",
    "ya": {
        "teks": "Suka pedas?",
        "harga": None,
        "deskripsi": "",
        "ya": {
            "teks": "Mau ayam?",
            "harga": None,
            "deskripsi": "",
            "ya": {
                "teks": "Ayam Geprek",
                "harga": 18000,
                "deskripsi": "Ayam goreng tepung diulek dengan sambal bawang",
                "ya": None,
                "tidak": None,
            },
            "tidak": {
                "teks": "Mie Goreng Pedas",
                "harga": 16000,
                "deskripsi": "Mie goreng level pedas + telur",
                "ya": None,
                "tidak": None,
            },
        },
        "tidak": {
            "teks": "Mau yang berkuah?",
            "harga": None,
            "deskripsi": "",
            "ya": {
                "teks": "Soto Ayam",
                "harga": 17000,
                "deskripsi": "Soto kuah kuning + nasi",
                "ya": None,
                "tidak": None,
            },
            "tidak": {
                "teks": "Nasi Goreng",
                "harga": 15000,
                "deskripsi": "Nasi goreng spesial telur",
                "ya": None,
                "tidak": None,
            },
        },
    },
    "tidak": {
        "teks": "Mau yang manis?",
        "harga": None,
        "deskripsi": "",
        "ya": {
            "teks": "Mau yang dingin?",
            "harga": None,
            "deskripsi": "",
            "ya": {
                "teks": "Es Krim Coklat",
                "harga": 12000,
                "deskripsi": "Es krim coklat 2 scoop + topping",
                "ya": None,
                "tidak": None,
            },
            "tidak": {
                "teks": "Coklat Panas",
                "harga": 10000,
                "deskripsi": "Coklat panas + marshmallow",
                "ya": None,
                "tidak": None,
            },
        },
        "tidak": {
            "teks": "Mau yang berkafein?",
            "harga": None,
            "deskripsi": "",
            "ya": {
                "teks": "Kopi Hitam",
                "harga": 8000,
                "deskripsi": "Kopi tubruk panas",
                "ya": None,
                "tidak": None,
            },
            "tidak": {
                "teks": "Air Mineral",
                "harga": 5000,
                "deskripsi": "Air mineral dingin 600ml",
                "ya": None,
                "tidak": None,
            },
        },
    },
}
