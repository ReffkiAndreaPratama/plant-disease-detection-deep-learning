"""Entry point pelatihan PlantVision AI (Sesi 2).

Alur:
1. Cek dataset (folder data/dataset/{train,val,test}).
2. Latih CNN/transfer learning ringan.
3. Evaluasi pada data uji.
4. Simpan model ke models/model_cnn.pt + metadata.json.

Jalankan dari folder proyek:
    python train.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.training import DATASET_DIR, latih  # noqa: E402


def main() -> int:
    print("=" * 70)
    print("PlantVision AI - Pelatihan CNN (Sesi 2)")
    print("=" * 70)

    if not (DATASET_DIR / "train").exists():
        print(f"[ERROR] Dataset tidak ditemukan: {DATASET_DIR}")
        print("Jalankan dulu: python scripts/prepare_dataset.py")
        return 1

    hasil = latih(verbose=True)

    print("\nRingkasan:")
    print(f"  Akurasi train     : {hasil['akurasi_train']:.4f}")
    print(f"  Akurasi validasi  : {hasil['akurasi_validasi']:.4f}")
    print(f"  Akurasi test      : {hasil['akurasi_test']:.4f}")
    print(f"  Precision (macro) : {hasil['metrik']['precision_macro']:.4f}")
    print(f"  Recall (macro)    : {hasil['metrik']['recall_macro']:.4f}")
    print(f"  F1 (macro)        : {hasil['metrik']['f1_macro']:.4f}")
    print(f"  Jumlah kelas      : {len(hasil['kelas'])}")
    print("\nModel tersimpan di models/model_cnn.pt")
    print("Jalankan aplikasi: streamlit run app.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
