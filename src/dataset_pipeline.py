"""
dataset_pipeline.py
===================
Menyiapkan dataset daun untuk klasifikasi.

Dua jalur (otomatis dipilih):
  1. `plantvillage`  : mengunduh subset kecil (36 gambar/kelas) dari dataset
                       PlantVillage di HuggingFace (mohanty/PlantVillage).
                       -> akurasi nyata pada foto daun sungguhan.
  2. `sintetik`      : jika tidak ada internet / unduhan gagal, membuat dataset
                       sintetik prosedural (gambar daun digambar program yang
                       diberi pola penyakit). -> aplikasi tetap berfungsi offline.

Struktur setelah persiapan:
  data/raw/<Kelas>/...          bahan mentah (hasil unduh / sintesis)
  data/dataset/{train,val,test}/<Kelas>/...  dataset siap latih (ImageFolder)
  data/meta_dataset.json        info sumber & statistik
"""

from __future__ import annotations

import io
import json
import math
import os
import random
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

try:
    from src import knowledge
except ImportError:  # pragma: no cover - fallback saat dijalankan sebagai script
    import knowledge

# =========================================================
# KONFIGURASI
# =========================================================


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
DATASET_DIR = DATA_DIR / "dataset"
META_FILE = DATA_DIR / "meta_dataset.json"

HF_MIRROR = "https://github.com/spMohanty/PlantVillage-Dataset"
# daftar path gambar (relatif) - file teks kecil dari repo HuggingFace
HF_SPLIT_TRAIN = "https://huggingface.co/datasets/mohanty/PlantVillage/resolve/main/splits/color_train.txt"
HF_SPLIT_TEST = "https://huggingface.co/datasets/mohanty/PlantVillage/resolve/main/splits/color_test.txt"
# host file gambar asli (isi repo spMohanty/PlantVillage-Dataset)
GH_RAW_BASE = "https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master"

TRAIN_PER_CLASS = 24
VAL_PER_CLASS = 6
TEST_PER_CLASS = 6

IMG_SIZE = 128          # ukuran input CNN
DOWNLOAD_WORKERS = 8
SEED = 42

# Nama kelas = urutan label yang konsisten (sama dengan knowledge.py)
KELAS = list(knowledge.PENGETAHUAN.keys())
KLAS_TO_INDEX = {k: i for i, k in enumerate(KELAS)}
INDEX_TO_KLAS = {i: k for i, k in enumerate(KELAS)}


# =========================================================
# UTILITAS
# =========================================================

def _hdr():
    return {"User-Agent": "Mozilla/5.0 (plant-doctor; educational)"}


def _unduh_bytes(url: str, timeout: int = 45) -> bytes:
    req = Request(url, headers=_hdr())
    with urlopen(req, timeout=timeout) as r:
        return r.read()


def _validasi_gambar(data: bytes) -> bool:
    try:
        Image.open(io.BytesIO(data)).verify()
        return True
    except Exception:
        return False


def _amat_dataset() -> tuple[str, dict]:
    """Membaca sumber dataset yang terakhir disiapkan."""
    if META_FILE.exists():
        meta = json.loads(META_FILE.read_text(encoding="utf-8"))
        return meta.get("sumber", "belum"), meta
    return "belum", {}


# =========================================================
# JALUR 1 - PLANTVILLAGE (SPLIT LIST + GITHUB RAW)
# =========================================================

def _daftar_path_semua() -> list[str]:
    """Gabungan daftar path dari split train + test PlantVillage (tanpa duplikat)."""
    semua: list[str] = []
    terlihat: set[str] = set()
    for url in (HF_SPLIT_TRAIN, HF_SPLIT_TEST):
        data = _unduh_bytes(url, timeout=90).decode("utf-8")
        for line in data.splitlines():
            line = line.strip()
            if not line:
                continue
            if line not in terlihat:
                terlihat.add(line)
                semua.append(line)
    return semua


def _unduh_subset_plantvillage() -> dict:
    """
    Mengunduh subset kecil PlantVillage (36 gambar/kelas) dari mirror GitHub.
    Mengembalikan dict kelas -> jumlah terunduh. Kelas yang gagal dikosongkan.
    """
    paths = _daftar_path_semua()
    per_kelas: dict[str, list[str]] = {}
    for p in paths:
        bagian = p.split("/")
        if len(bagian) >= 4 and bagian[0] == "raw" and bagian[1] == "color":
            per_kelas.setdefault(bagian[2], []).append(p)

    perolehan: dict[str, int] = {}
    target = TRAIN_PER_CLASS + VAL_PER_CLASS + TEST_PER_CLASS
    with ThreadPoolExecutor(max_workers=DOWNLOAD_WORKERS) as pool:
        for kode_kelas in KELAS:
            folder_raw = RAW_DIR / kode_kelas
            folder_raw.mkdir(parents=True, exist_ok=True)
            for f in folder_raw.iterdir():
                f.unlink()
            pilihan = per_kelas.get(kode_kelas, [])[:target]
            hasil: dict[str, Path] = {}

            def satu(rel: str):
                nama = Path(rel.split("/")[-1]).name
                dest = folder_raw / nama
                if dest.exists() and dest.stat().st_size > 1000:
                    return rel, dest
                url = f"{GH_RAW_BASE}/{quote(rel, safe='/')}"
                try:
                    data = _unduh_bytes(url)
                except Exception:
                    return rel, None
                if not _validasi_gambar(data):
                    return rel, None
                dest.write_bytes(data)
                return rel, dest

            futures = [pool.submit(satu, p) for p in pilihan]
            for fut in as_completed(futures):
                _, dest = fut.result()
                if dest is not None:
                    hasil[dest.name] = dest

            perolehan[kode_kelas] = len(hasil)
            if len(hasil) < target:
                for f in folder_raw.glob("*"):
                    f.unlink()
    return perolehan


# =========================================================
# JALUR 2 - DATASET SINTETIK (OFFLINE)
# =========================================================

# gaya visual tiap kelas (kunci penyakit)
_GAYA_DAUN = {
    "Apple___Apple_scab": "scab",
    "Apple___Black_rot": "blackrot",
    "Apple___Cedar_apple_rust": "rust",
    "Apple___healthy": "sehat",
    "Blueberry___healthy": "sehat",
    "Cherry_(including_sour)___Powdery_mildew": "mildew",
    "Cherry_(including_sour)___healthy": "sehat",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "cercospora",
    "Corn_(maize)___Common_rust_": "rust",
    "Corn_(maize)___Northern_Leaf_Blight": "hawar",
    "Corn_(maize)___healthy": "sehat",
    "Grape___Black_rot": "blackrot",
    "Grape___Esca_(Black_Measles)": "esca",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "blight",
    "Grape___healthy": "sehat",
    "Orange___Haunglongbing_(Citrus_greening)": "greening",
    "Peach___Bacterial_spot": "bakteri",
    "Peach___healthy": "sehat",
    "Pepper,_bell___Bacterial_spot": "bakteri",
    "Pepper,_bell___healthy": "sehat",
    "Potato___Early_blight": "earlyblight",
    "Potato___Late_blight": "lateblight",
    "Potato___healthy": "sehat",
    "Raspberry___healthy": "sehat",
    "Soybean___healthy": "sehat",
    "Squash___Powdery_mildew": "mildew",
    "Strawberry___Leaf_scorch": "scorch",
    "Strawberry___healthy": "sehat",
    "Tomato___Bacterial_spot": "bakteri",
    "Tomato___Early_blight": "earlyblight",
    "Tomato___Late_blight": "lateblight",
    "Tomato___Leaf_Mold": "leafmold",
    "Tomato___Septoria_leaf_spot": "septoria",
    "Tomato___Spider_mites Two-spotted_spider_mite": "tungau",
    "Tomato___Target_Spot": "target",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "curl",
    "Tomato___Tomato_mosaic_virus": "mosaic",
    "Tomato___healthy": "sehat",
}

# bentuk dasar daun per kelas (kompak agar mudah)
_BENTUK_DAUN = {
    "Apple": "lancip",
    "Blueberry": "oval",
    "Cherry": "lanset",
    "Corn": "pita",
    "Grape": "cuping",
    "Orange": "oval",
    "Peach": "lanset",
    "Pepper": "oval",
    "Potato": "majemuk",
    "Raspberry": "majemuk",
    "Soybean": "oval",
    "Squash": "cuping",
    "Strawberry": "lanset",
    "Tomato": "majemuk",
}


def _gambar_poligon_gelombang(draw, pts, jitter, rng, warna: tuple, outline=None):
    """Gambar poligon dengan jitter di tepi agar tampak organik."""
    n = len(pts)
    baru = []
    for i, (x, y) in enumerate(pts):
        dx = rng.uniform(-jitter, jitter)
        dy = rng.uniform(-jitter, jitter)
        baru.append((x + dx, y + dy))
    draw.polygon(baru, fill=warna, outline=outline)


def _titik_oval(cx, cy, rx, ry, rng, n=48, bergerigi=0.0):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        r = math.sqrt(abs(rng.gauss(1.0, 0.10)))
        x = cx + rx * r * math.cos(t)
        y = cy + ry * r * math.sin(t)
        pts.append((x, y))
    return pts


def _titik_lanset(cx, cy, panjang, rng, n=40):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = cx + panjang * math.cos(t)
        y = cy + (panjang * 0.38) * math.sin(t) * (1 + 0.18 * math.sin(2 * t))
        if x > cx + (panjang * 0.85) and y > cy - 30:
            y += 45 * abs(math.sin(t - math.pi / 2))  # ujung lancip bawah
        pts.append((x + rng.uniform(-4, 4), y + rng.uniform(-4, 4)))
    return pts


def _titik_pita(cx, cy, panjang, rng, n=40):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        x = cx + panjang * math.cos(t)
        y_ = cy + (panjang * 0.16) * math.sin(t) * (1 + 0.25 * math.sin(3 * t))
        pts.append((x + rng.uniform(-3, 3), y_ + rng.uniform(-3, 3)))
    return pts


def _titik_cuping(cx, cy, rx, ry, rng, n=56):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        lobe = 1.0 + 0.23 * math.cos(3 * (t - math.pi / 2))
        x = cx + rx * lobe * math.cos(t)
        y = cy + ry * lobe * math.sin(t)
        pts.append((x + rng.uniform(-4, 4), y + rng.uniform(-4, 4)))
    return pts


def _titik_majemuk(gambar, rng, warna_daun, warna_urat):
    """Daun majemuk: sumbu utama + 4-5 anak daun kecil."""
    draw = ImageDraw.Draw(gambar)
    cx, cy = 128, 148
    batang = [(cx, cy + 50), (cx, cy - 45)]
    draw.line(batang, fill=warna_urat, width=5 + int(rng.uniform(0, 3)))

    for i in range(5):
        y = cy + 30 - i * 20
        side = 1 if i % 2 == 0 else -1
        el = rng.uniform(0.8, 1.2)
        x0 = cx + side * 34 * el
        rx, ry = 26 * el, 16
        pts = _titik_oval(x0, y, rx, ry, rng, n=32, bergerigi=1.5)
        r, g, b = warna_daun
        r = max(0, min(255, r + int(rng.uniform(-14, 14))))
        g = max(0, min(255, g + int(rng.uniform(-14, 14))))
        b = max(0, min(255, b + int(rng.uniform(-14, 14))))
        _gambar_poligon_gelombang(draw, pts, 2.0, rng, (r, g, b), outline=warna_urat)
        draw.line([[cx + 8 * side, y], [x0 + side * 6, y]], fill=warna_urat, width=2)


def _gambar_daun_bangun(shape: str, rng, warna_daun, warna_urat) -> Image.Image:
    """Menggambar satu daun + tulang daun. Kembalikan citra RGB (kanvas kosong)."""
    img = Image.new("RGB", (256, 256), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    r, g, b = warna_daun

    if shape == "pita":
        pts = _titik_pita(128, 148, 96, rng)
    elif shape == "lanset":
        pts = _titik_lanset(128, 148, 88, rng)
    elif shape == "cuping":
        pts = _titik_cuping(128, 148, 78, 92, rng)
    else:  # oval / lancip / majemuk pakai oval dasarnya dulu
        pts = _titik_oval(128, 148, 78, 84, rng, bergerigi=2 if shape == "lancip" else 0)

    _gambar_poligon_gelombang(
        draw, pts, 2.5, rng, (r, g, b), outline=(int(r * 0.7), int(g * 0.8), int(b * 0.6))
    )
    # tulang daun tengah
    mini = Image.new("L", (256, 256), 0)
    drawm = ImageDraw.Draw(mini)
    drawm.line([(128, 62), (128, 232)], fill=255, width=3)
    for i in range(6):
        yy = 80 + i * 26
        drawm.line([(128, yy), (128 - 42 - i * 3, yy + 14)], fill=255, width=2)
        drawm.line([(128, yy), (128 + 42 + i * 3, yy + 14)], fill=255, width=2)
    vein = Image.composite(
        Image.new("RGB", (256, 256), warna_urat), img, mini.filter(ImageFilter.GaussianBlur(1))
    )
    img = Image.composite(vein, img, mini.point(lambda p: 255 if p > 128 else 0))
    return img


def _overlay_dalam_daun(img: Image.Image, warna) -> Image.Image:
    """Tumpuk warna hanya dalam citra daun (bukan background hitam)."""
    gray = np.array(img.convert("L"))
    mask = gray > 25
    arr = np.array(img).astype(np.int16)
    added = np.asarray(warna, dtype=np.int16).reshape(1, 1, 3)
    arr[mask] = arr[mask] + added
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def _warna_penyakit(style: str) -> tuple:
    pemetaan = {
        "scab": (60, 84, 58),
        "blackrot": (70, 46, 38),
        "rust": (168, 92, 8),
        "mildew": (235, 240, 235),
        "cercospora": (96, 88, 88),
        "hawar": (112, 70, 40),
        "blight": (120, 84, 50),
        "esca": (150, 70, 80),
        "greening": (190, 190, 40),
        "bakteri": (70, 84, 40),
        "earlyblight": (104, 68, 40),
        "lateblight": (50, 60, 50),
        "leafmold": (100, 84, 50),
        "septoria": (120, 104, 88),
        "tungau": (225, 230, 160),
        "target": (90, 60, 44),
        "curl": (150, 160, 60),
        "mosaic": (140, 170, 90),
        "scorch": (110, 60, 50),
    }
    return pemetaan.get(style, (80, 80, 60))


def _gambar_gejala(img: Image.Image, style: str, rng) -> Image.Image:
    """Suntikkan pola penyakit sesuai style."""
    gray = np.array(img.convert("L"))
    mask = gray > 25
    arr = np.array(img).astype(np.int16)
    warna = _warna_penyakit(style)
    wr, wg, wb = warna
    n_spot = rng.randint(14, 40)
    ukuran = 3

    if style == "sehat":
        arr[mask] = arr[mask] + np.array([rng.randint(-6, 6), rng.randint(0, 12), rng.randint(-6, 6)])
    elif style == "scab":
        warna_sp = (52, 66, 48)
        for _ in range(n_spot):
            x = rng.randint(30, 225)
            y = rng.randint(30, 225)
            r = rng.randint(ukuran, ukuran + 6)
            for rr in range(r):
                yy, xx = np.ogrid[-rr:rr + 1, -rr:rr + 1]
                c = mask[y - rr:y + rr + 1, x - rr:x + rr + 1]
                if c.any():
                    bm = np.zeros_like(mask, dtype=bool)
                    bm[max(0, y - rr):y + rr + 1, max(0, x - rr):x + rr + 1] = xx ** 2 + yy ** 2 - rr * 2 <= 0
                    bm = bm & mask
                    arr[bm] = arr[bm] * 0.55 + np.array(warna_sp, dtype=np.int16) * 0.45
    elif style in ("bakteri", "earlyblight", "blackrot", "target", "septoria", "hawar"):
        for _ in range(n_spot):
            x = rng.randint(35, 220)
            y = rng.randint(35, 220)
            r = rng.randint(3, 8 if style != "septoria" else 5)
            bm = np.zeros_like(mask, dtype=bool)
            yy, xx = np.ogrid[-2 * r:2 * r + 1, -2 * r:2 * r + 1]
            disc = (xx / (1.35 * r)) ** 2 + (yy / r) ** 2 <= 1
            bm[max(0, y - 2 * r):y + 2 * r + 1, max(0, x - 2 * r):x + 2 * r + 1] = disc
            bm = bm & mask
            arr[bm] = arr[bm] * 0.5 + np.array(warna, dtype=np.int16) * 0.5
            if style in ("earlyblight", "target"):
                # cincin konsentris tipis
                hal = (int(wr * 0.9), int(wg * 0.9), int(wb * 0.9))
                ring = bm & ~np.roll(bm, 1, axis=0)
                arr[ring] = np.array((210, 205, 160), dtype=np.int16)
    elif style == "lateblight":
        for _ in range(3):
            x = rng.randint(35, 220)
            y = rng.randint(35, 220)
            rx, ry = rng.randint(20, 45), rng.randint(16, 38)
            bm = np.zeros_like(mask, dtype=bool)
            yy, xx = np.ogrid[-ry:ry + 1, -rx:rx + 1]
            disc = (xx / rx) ** 2 + (yy / ry) ** 2 <= 1
            bm[max(0, y - ry):y + ry + 1, max(0, x - rx):x + rx + 1] = disc
            bm = bm & mask
            arr[bm] = arr[bm] * 0.4 + np.array(warna, dtype=np.int16) * 0.6
    elif style in ("mildew", "leafmold"):
        for _ in range(6):
            x = rng.randint(35, 220)
            y = rng.randint(35, 220)
            rx, ry = rng.randint(14, 34), rng.randint(8, 22)
            bm = np.zeros_like(mask, dtype=bool)
            yy, xx = np.ogrid[-ry:ry + 1, -rx:rx + 1]
            disc = (xx / rx) ** 2 + (yy / ry) ** 2 <= 1
            bm[max(0, y - ry):y + ry + 1, max(0, x - rx):x + rx + 1] = disc
            bm = bm & mask
            arr[bm] = arr[bm] * 0.35 + np.array(warna, dtype=np.int16) * 0.65
    elif style == "rust":
        for _ in range(n_spot):
            x = rng.randint(30, 225)
            y = rng.randint(30, 225)
            r = rng.randint(3, 6)
            bm = np.zeros_like(mask, dtype=bool)
            yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
            disc = xx ** 2 + yy ** 2 <= r * r
            bm[max(0, y - r):y + r + 1, max(0, x - r):x + r + 1] = disc
            bm = bm & mask
            arr[bm] = np.array((150, 60, 10), dtype=np.int16)
    elif style == "cercospora":
        for _ in range(n_spot):
            y = rng.randint(50, 210)
            x0 = rng.randint(20, 60)
            xr = rng.randint(30, 60)
            bm = np.zeros_like(mask, dtype=bool)
            for xx in range(0, xr, 2):
                x = x0 + xx
                bm[max(0, y - 2):y + 3, max(0, x - 2):x + 3] = True
            bm = bm & mask
            arr[bm] = np.array(warna, dtype=np.int16)
    elif style == "esca":
        for _ in range(30):
            x = rng.randint(40, 215)
            y = rng.randint(40, 215)
            r = rng.randint(2, 4)
            bm = np.zeros_like(mask, dtype=bool)
            yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
            disc = xx ** 2 + yy ** 2 <= r * r
            bm[max(0, y - r):y + r + 1, max(0, x - r):x + r + 1] = disc
            bm = bm & mask
            arr[bm] = np.array((150, 50, 60), dtype=np.int16)
    elif style == "greening":
        for _ in range(25):
            x = rng.randint(45, 210)
            y = rng.randint(45, 210)
            r = rng.randint(4, 10)
            bm = np.zeros_like(mask, dtype=bool)
            yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
            disc = xx ** 2 + yy ** 2 <= r * r
            bm[max(0, y - r):y + r + 1, max(0, x - r):x + r + 1] = disc
            bm = bm & mask
            arr[bm] = np.array((210, 215, 80), dtype=np.int16)
    elif style == "tungau":
        arr[mask] = arr[mask] + np.array([10, 14, 4])
        for _ in range(int(n_spot * 4)):
            x = rng.randint(30, 225)
            y = rng.randint(30, 225)
            arr[max(0, y - 1):y + 2, max(0, x - 1):x + 2] = (245, 245, 220)
    elif style == "scorch":
        bm = np.zeros_like(mask, dtype=bool)
        bm[:24, :] = True
        bm[232:, :] = True
        bm[:, :24] = True
        bm[:, 232:] = True
        bm = bm & mask
        bm = np.array(Image.fromarray(bm).filter(ImageFilter.GaussianBlur(3)))
        arr[bm > 60] = arr[bm > 60] * 0.45 + np.array(warna, dtype=np.int16) * 0.55
    elif style == "curl":
        # pinggiran menguning + lengkung tepi
        bm = np.zeros_like(mask, dtype=bool)
        bm[:18, :] = True
        bm[238:, :] = True
        bm[:, :18] = True
        bm[:, 238:] = True
        bm = bm & mask
        bm = np.array(Image.fromarray(bm.astype(np.uint8) * 255).filter(ImageFilter.GaussianBlur(2))) > 80
        arr[bm] = np.array((200, 205, 90), dtype=np.int16)
        # bentuk daun dikerutkan
    elif style == "mosaic":
        bm = np.zeros_like(mask, dtype=bool)
        for _ in range(14):
            x = rng.randint(40, 215)
            y = rng.randint(40, 215)
            rx, ry = rng.randint(7, 16), rng.randint(5, 12)
            yy, xx = np.ogrid[-ry:ry + 1, -rx:rx + 1]
            disc = (xx / rx) ** 2 + (yy / ry) ** 2 <= 1
            bm[max(0, y - ry):y + ry + 1, max(0, x - rx):x + rx + 1] = disc
        bm = bm & mask
        arr[bm] = arr[bm] * 0.55 + np.array((150, 180, 90), dtype=np.int16)

    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(0.6)
    )


def buat_satu_gambar(kode_kelas: str, seed: int, ukuran: int = 256) -> Image.Image:
    """Generate satu citra sintetik untuk kelas tertentu."""
    rng = random.Random(seed * 7919)
    npr = np.random.default_rng(seed)

    shape = _BENTUK_DAUN.get(kode_kelas.split("___")[0], "oval")
    style = _GAYA_DAUN[kode_kelas]

    hijau_dasar = (34 + rng.randint(0, 14), 116 + rng.randint(0, 30), 34 + rng.randint(0, 9))
    warna_urat = (46, 88, 46)
    if style == "greening":
        warna_urat = (150, 160, 60)

    kanvas = Image.new("RGB", (256, 256), (0, 0, 0))
    if shape != "majemuk":
        daun = _gambar_daun_bangun(shape, rng, hijau_dasar, warna_urat)
        kanvas = Image.composite(daun, kanvas, Image.new("L", (256, 256), 255))
    else:
        _titik_majemuk(kanvas, rng, hijau_dasar, warna_urat)

    # sedikit degradasi warna daun
    arr = np.array(kanvas).astype(np.int16)
    gray = arr.mean(axis=2) > 25
    arr[gray] = arr[gray] + npr.integers(-9, 9, size=arr[gray].shape)
    kanvas = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    kanvas = _gambar_gejala(kanvas, style, rng)

    # latar belakang (panel/bantu deteksi)
    bg = Image.new("RGB", (256, 256), (0, 0, 0))
    arr_bg = np.zeros((256, 256, 3), dtype=np.int16)
    arr_bg[:, :] = (190, 185, 172) if rng.random() < 0.75 else (225, 224, 218)
    arr_bg = arr_bg + npr.integers(-8, 8, size=arr_bg.shape)
    arr_bg = np.clip(arr_bg, 0, 255).astype(np.uint8)
    bg = Image.fromarray(arr_bg)

    # rotasi + geser acak
    sudut = rng.uniform(-180, 180)
    daunda = kanvas.rotate(sudut, resample=Image.BICUBIC, expand=False)
    pos = (rng.randint(-24, 24), rng.randint(-24, 24))
    gabung = bg.copy()
    gabung.paste(daunda, pos, Image.eval(daunda.convert("L"), lambda v: 255 if v > 25 else 0))

    # noise + vignette
    arr = np.array(gabung).astype(np.int16)
    arr = arr + npr.integers(-12, 12, size=arr.shape)
    yy, xx = np.mgrid[0:256, 0:256]
    cen = np.sqrt((xx - 128) ** 2 + (yy - 128) ** 2)
    faktor = 1 - 0.25 * (cen / 128) ** 2
    arr = arr * faktor[..., None]
    gabung = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    return gabung.resize((ukuran, ukuran), Image.LANCZOS)


def _hasilkan_sintetik_kelas(kode: str, tambahan: int) -> int:
    """Membuat gambar sintetik untuk satu kelas. Mengembalikan jumlah yang dibuat."""
    folder = RAW_DIR / kode
    folder.mkdir(parents=True, exist_ok=True)
    idx_base = KLAS_TO_INDEX[kode] * 1000
    mulai = sum(1 for _ in folder.glob("*"))
    n_buat = 0
    for i in range(mulai, mulai + tambahan):
        img = buat_satu_gambar(kode, seed=idx_base + i)
        img.save(folder / f"sintetik_{i:03d}.png")
        n_buat += 1
    return n_buat


# =========================================================
# SPLIT + PENYIAPAN AKHIR
# =========================================================

def _bersihkan_dataset_dir():
    if DATASET_DIR.exists():
        shutil.rmtree(DATASET_DIR)
    for sub in ("train", "val", "test"):
        (DATASET_DIR / sub).mkdir(parents=True, exist_ok=True)


def _salin_split():
    """Salin dari data/raw ke data/dataset dalam split train/val/test."""
    for kode in KELAS:
        folder_raw = RAW_DIR / kode
        if not folder_raw.exists():
            continue
        files = sorted(p for p in folder_raw.iterdir() if p.is_file())
        if len(files) < TRAIN_PER_CLASS + VAL_PER_CLASS + TEST_PER_CLASS:
            continue
        random.Random(SEED).shuffle(files)
        n_tr = TRAIN_PER_CLASS
        for sub, subset in (
            ("train", files[:n_tr]),
            ("val", files[n_tr:n_tr + VAL_PER_CLASS]),
            ("test", files[n_tr + VAL_PER_CLASS: n_tr + VAL_PER_CLASS + TEST_PER_CLASS]),
        ):
            tujuan = DATASET_DIR / sub / kode
            tujuan.mkdir(parents=True, exist_ok=True)
            for f in subset:
                shutil.copy2(f, tujuan / f.name)


def statistik_dataset() -> dict:
    """Statistik dataset yang sudah disiapkan (untuk UI & laporan)."""
    n_kelas = 0
    per_kelas: dict[str, int] = {}
    total = 0
    for kode in KELAS:
        folder = DATASET_DIR / "train" / kode
        if folder.exists():
            n = len([f for f in folder.iterdir() if f.suffix.lower() in (".jpg", ".jpeg", ".png")])
            per_kelas[kode] = n
            total += n
            n_kelas += 1
    return {
        "sumber": _amat_dataset()[0],
        "jumlah_kelas": n_kelas,
        "jumlah_gambar_train": total,
        "per_kelas": per_kelas,
    }


def persiapkan(progress=None, status=None, verbose: bool = True) -> dict:
    """
    Menyiapkan dataset (unduh PlantVillage dari GitHub, fallback sintetik)
    lalu membuat fold train/val/test. `progress` = callable(0-100) untuk UI,
    `status` = callable(str) untuk status.

    Mengembalikan dict ringkasan {sumber, n_kelas, n_gambar, sudah_ada, meta}.
    """
    perlu = TRAIN_PER_CLASS + VAL_PER_CLASS + TEST_PER_CLASS

    if status:
        status("Memeriksa dataset yang sudah ada...")
    meta = _amat_dataset()[1]
    if meta and (DATASET_DIR / "train").exists() and any((DATASET_DIR / "train").iterdir()):
        return {
            "sumber": meta.get("sumber"),
            "n_kelas": len(meta.get("kelas", {})),
            "n_gambar": sum(meta.get("kelas", {}).values()),
            "sudah_ada": True,
            "meta": meta,
        }

    if status:
        status("Mengunduh subset PlantVillage dari GitHub mirror (spMohanty)...")
    if progress:
        progress(5)
    perolehan = _unduh_subset_plantvillage()
    n_real = sum(v for v in perolehan.values() if v >= perlu)
    n_short = sum(1 for v in perolehan.values() if v < perlu)
    if verbose:
        print(f"  Unduhan real: {n_real}/{len(KELAS)} kelas cukup; {n_short} kelas kurang.")

    if n_real == 0:
        if status:
            status("Tidak dapat mengunduh data asli. Beralih ke dataset sintetik.")
        for kode in KELAS:
            _hasilkan_sintetik_kelas(kode, perlu)
        sumber = "sintetik"
    elif n_short > 0:
        if status:
            status(f"Melengkapi {n_short} kelas kurang dengan data sintetik...")
        for kode in KELAS:
            kurang = perlu - perolehan.get(kode, 0)
            if kurang > 0:
                _hasilkan_sintetik_kelas(kode, kurang)
        sumber = "hibrida"
    else:
        sumber = "plantvillage"

    if progress:
        progress(70)
    if status:
        status("Menyusun split train/val/test...")
    _bersihkan_dataset_dir()
    _salin_split()

    total_per = {}
    for kode in KELAS:
        f = RAW_DIR / kode
        total_per[kode] = sum(1 for _ in f.iterdir()) if f.exists() else 0

    meta_out = {"sumber": sumber, "asal": HF_MIRROR if sumber != "sintetik" else "sintetik", "kelas": total_per}
    META_FILE.write_text(
        json.dumps(meta_out, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    if progress:
        progress(100)
    return {
        "sumber": sumber,
        "n_kelas": len(KELAS),
        "n_gambar": sum(total_per.values()),
        "sudah_ada": False,
        "meta": meta_out,
    }


if __name__ == "__main__":
    r = persiapkan()
    print("Sumber:", r["sumber"])
    print("Kelas:", r["n_kelas"])
    print("Gambar:", r["n_gambar"])