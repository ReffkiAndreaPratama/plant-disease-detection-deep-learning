"""Menyiapkan dataset daun untuk PlantVision AI (Sesi 2).

Mengunduh subset kecil PlantVillage (spMohanty mirror) bila internet tersedia,
atau membuat dataset sintetik prosedural sebagai fallback offline. Dataset hasil
disusun ke data/dataset/{train,val,test}/<Kelas> siap dipakai ImageFolder.

Jalankan:
    python scripts/prepare_dataset.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.dataset_pipeline import persiapkan  # noqa: E402


def main() -> int:
    print("=" * 70)
    print("PlantVision AI - Persiapan Dataset (Sesi 2)")
    print("=" * 70)
    hasil = persiapkan(
        progress=lambda p: print(f"  [{p:3.0f}%]", end="\r"),
        status=lambda s: print(f"  {s}"),
        verbose=True,
    )
    print()
    print("Selesai:")
    print(f"  Sumber     : {hasil['sumber']}")
    print(f"  Jumlah kelas: {hasil['n_kelas']}")
    print(f"  Jumlah gambar: {hasil['n_gambar']}")
    if hasil.get("sudah_ada"):
        print("  (dataset sudah ada sebelumnya, tidak diunduh ulang)")
    print("\nLanjutkan: python train.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
