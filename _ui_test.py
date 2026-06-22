"""Uji headless: konstruksi app + gambar canvas + alur pandu. Dihapus setelah uji."""
import tkinter as tk
import main, tree

try:
    root = tk.Tk()
except tk.TclError as e:
    print("SKIP: tak ada display di sandbox ->", e)
    raise SystemExit(0)

main.apply_light_theme(root)
app = main.PemanduApp(root)

# Paksa gambar pohon
app.gambar_pohon()
print("node tergambar (punya bbox):", len(app.node_bbox))
assert len(app.node_bbox) == 15, "harusnya 15 node tergambar"

# Cek tiap node punya posisi & bbox masuk akal
pos = app._hitung_posisi()
assert len(pos) == 15
xs = [bbox for bbox in app.node_bbox.values()]
assert all(x1 < x2 and y1 < y2 for (x1, y1, x2, y2) in xs), "bbox valid"

# Simulasikan Pandu Pesan: jawab Ya terus sampai daun
app.aksi_pandu()
node = app.akar
langkah = 0
while not node.is_menu():
    app._pandu_maju(node, node.ya)
    node = node.ya
    langkah += 1
print(f"pandu (semua-Ya) -> '{node.teks}' setelah {langkah} pertanyaan")
assert node.is_menu()
assert node in app.highlight, "daun hasil harus ter-sorot"
assert len(app.highlight) == langkah + 1, "jalur ter-sorot = pertanyaan + daun"

# Klik simulasi: pilih sebuah node lewat hit-test koordinat tengahnya
target = next(n for n in tree.preorder(app.akar) if n.is_menu())
x1, y1, x2, y2 = app.node_bbox[target]
class _Ev:  # objek event palsu
    pass
ev = _Ev(); ev.x = (x1 + x2) / 2; ev.y = (y1 + y2) / 2
app._on_click(ev)
assert app.selected is target, "klik di tengah node harus memilih node itu"
print("klik-pilih node OK ->", app.selected.teks)

# Keluar pandu & refresh
app._keluar_pandu()
assert app.highlight == set()

print("UI HEADLESS OK ✓ (gambar, pandu, klik-pilih jalan tanpa error)")
root.destroy()
