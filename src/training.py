"""Pelatihan, evaluasi, dan prediksi model CNN daun (Sesi 2).

Modul ini menyatukan:
- Loader dataset (ImageFolder train/val/test).
- Augmentasi & preprocessing.
- Pelatihan dengan early stopping.
- Evaluasi (accuracy, precision, recall, F1, confusion matrix).
- Simpan/muat model.
- Prediksi satu/beberapa citra + Grad-CAM (Explainable AI).

Semua metrik dihitung dari hasil prediksi model yang sebenarnya.
"""

from __future__ import annotations

import json
import random
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from PIL import Image
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from src.model import IMAGENET_MEAN, IMAGENET_STD, IMG_SIZE, ModelKlasifikasiDaun, jumlah_param

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_DIR = BASE_DIR / "data" / "dataset"
MODEL_DIR = BASE_DIR / "models"
CKPT = MODEL_DIR / "model_cnn.pt"
METADATA_FILE = MODEL_DIR / "metadata.json"

BATCH_SIZE = 32
EPOCHS_DEFAULT = 14
LR_DEFAULT = 1e-3
SEED = 42
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

try:
    torch.set_num_threads(1)
except Exception:
    pass

NORMALIZE = transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD)


def _seed() -> None:
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)


def transform_train(size: int = IMG_SIZE) -> transforms.Compose:
    return transforms.Compose(
        [
            transforms.Resize((size, size)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(12),
            transforms.ColorJitter(0.12, 0.12, 0.12),
            transforms.ToTensor(),
            NORMALIZE,
        ]
    )


def transform_eval(size: int = IMG_SIZE) -> transforms.Compose:
    return transforms.Compose(
        [transforms.Resize((size, size)), transforms.ToTensor(), NORMALIZE]
    )


def build_loaders(batch_size: int = BATCH_SIZE):
    """Membangun DataLoader untuk train/val/test dari folder dataset."""
    if not (DATASET_DIR / "train").exists():
        raise FileNotFoundError(
            f"Dataset tidak ditemukan di '{DATASET_DIR}'. "
            "Jalankan: python scripts/prepare_dataset.py"
        )
    train_ds = datasets.ImageFolder(DATASET_DIR / "train", transform=transform_train())
    val_ds = datasets.ImageFolder(DATASET_DIR / "val", transform=transform_eval())
    test_ds = datasets.ImageFolder(DATASET_DIR / "test", transform=transform_eval())
    train_ld = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=0)
    val_ld = DataLoader(val_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    test_ld = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    return train_ld, val_ld, test_ld, train_ds.classes


@torch.no_grad()
def evaluasi_dasar(model, loader, criterion):
    model.eval()
    total, benar, rugi = 0, 0, 0.0
    for x, y in loader:
        x, y = x.to(DEVICE), y.to(DEVICE)
        out = model(x)
        rugi += criterion(out, y).item() * x.size(0)
        benar += (out.argmax(1) == y).sum().item()
        total += x.size(0)
    return rugi / total, benar / total


@torch.no_grad()
def confusion_matrix(model, loader, n_kelas: int) -> np.ndarray:
    mat = np.zeros((n_kelas, n_kelas), dtype=int)
    for x, y in loader:
        x = x.to(DEVICE)
        pred = model(x).argmax(1).cpu().numpy()
        for t, p in zip(y.numpy(), pred):
            mat[t, p] += 1
    return mat


def hitung_metrik(mat: np.ndarray) -> dict:
    """Menghitung accuracy, precision, recall, F1 (macro) dari confusion matrix."""
    total = mat.sum()
    accuracy = float(np.trace(mat) / total) if total else 0.0
    n = mat.shape[0]
    precisions, recalls, f1s = [], [], []
    for i in range(n):
        tp = mat[i, i]
        fp = mat[:, i].sum() - tp
        fn = mat[i, :].sum() - tp
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
        precisions.append(prec)
        recalls.append(rec)
        f1s.append(f1)
    return {
        "accuracy": accuracy,
        "precision_macro": float(np.mean(precisions)),
        "recall_macro": float(np.mean(recalls)),
        "f1_macro": float(np.mean(f1s)),
    }


def latih(
    epochs: int = EPOCHS_DEFAULT,
    lr: float = LR_DEFAULT,
    progress=None,
    verbose: bool = True,
) -> dict:
    """Melatih model dari dataset yang tersedia. Mengembalikan ringkasan hasil."""
    _seed()
    train_ld, val_ld, test_ld, nama_kelas = build_loaders()

    model = ModelKlasifikasiDaun(len(nama_kelas)).to(DEVICE)
    criterion = nn.CrossEntropyLoss()
    optim = torch.optim.Adam(model.parameters(), lr=lr)
    sched = torch.optim.lr_scheduler.ReduceLROnPlateau(optim, patience=3, factor=0.5)

    best_acc, best_state, tunggu = 0.0, None, 0
    riwayat = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    total = len(train_ld)

    for ep in range(1, epochs + 1):
        model.train()
        rugi, benar, n = 0.0, 0, 0
        for i, (x, y) in enumerate(train_ld, 1):
            x, y = x.to(DEVICE), y.to(DEVICE)
            optim.zero_grad()
            out = model(x)
            loss = criterion(out, y)
            loss.backward()
            optim.step()
            rugi += loss.item() * x.size(0)
            benar += (out.argmax(1) == y).sum().item()
            n += x.size(0)
            if progress:
                progress(5 + 85 * ((ep - 1 + i / total) / epochs))

        vl, va = evaluasi_dasar(model, val_ld, criterion)
        riwayat["train_loss"].append(rugi / n)
        riwayat["val_loss"].append(vl)
        riwayat["train_acc"].append(benar / n)
        riwayat["val_acc"].append(va)
        sched.step(vl)
        if verbose:
            print(
                f"epoch {ep:2d}/{epochs}  tr_acc {benar / n:.4f}  val_acc {va:.4f}  "
                f"tr_loss {rugi / n:.4f}  val_loss {vl:.4f}"
            )

        if va > best_acc:
            best_acc = va
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            tunggu = 0
        else:
            tunggu += 1
            if tunggu >= 5:
                if verbose:
                    print("Early stop.")
                break

    if best_state is None:
        best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}

    model.load_state_dict(best_state)
    test_ld_full = test_ld
    te_loss, te_acc = evaluasi_dasar(model, test_ld_full, criterion)
    mat = confusion_matrix(model, test_ld, len(nama_kelas))
    metrik = hitung_metrik(mat)

    info = {
        "epochs_dilatih": len(riwayat["train_loss"]),
        "epochs_total": epochs,
        "lr": lr,
        "batch_size": BATCH_SIZE,
        "akurasi_train": riwayat["train_acc"][-1],
        "akurasi_validasi": best_acc,
        "akurasi_test": te_acc,
        "loss_train_akhir": riwayat["train_loss"][-1],
        "loss_val_akhir": riwayat["val_loss"][-1],
        "jumlah_param": jumlah_param(model),
        "kelas": nama_kelas,
        "device": str(DEVICE),
        "metrik": metrik,
        "confusion_matrix": mat.tolist(),
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    torch.save({"state_dict": best_state, "kelas": nama_kelas, "info": info}, CKPT)
    METADATA_FILE.write_text(
        json.dumps({"model": info}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if progress:
        progress(100)

    return {
        "akurasi_train": riwayat["train_acc"][-1],
        "akurasi_validasi": best_acc,
        "akurasi_test": te_acc,
        "metrik": metrik,
        "riwayat": riwayat,
        "kelas": nama_kelas,
    }


_model_cache: dict = {}


def muat_model(segarkan: bool = False):
    """Memuat model + daftar kelas (di-cache dalam proses)."""
    if not segarkan and _model_cache:
        return _model_cache["model"], _model_cache["kelas"]
    _model_cache.clear()
    if not CKPT.exists():
        return None, None
    data = torch.load(CKPT, map_location="cpu", weights_only=False)
    kelas = data["kelas"]
    model = ModelKlasifikasiDaun(len(kelas))
    model.load_state_dict(data["state_dict"])
    model.eval()
    _model_cache["model"] = model
    _model_cache["kelas"] = kelas
    return model, kelas


def preprocessing(pil_image: Image.Image, size: int = IMG_SIZE) -> torch.Tensor:
    """Ubah PIL.Image -> tensor ter-normalisasi berukuran (1, 3, size, size)."""
    pil_image = pil_image.convert("RGB").resize((size, size), Image.LANCZOS)
    return NORMALIZE(transforms.ToTensor()(pil_image)).unsqueeze(0)


def prediksi(pil_image: Image.Image, n_top: int = 3) -> dict | None:
    """Mengembalikan prediksi top-N untuk satu citra."""
    model, kelas = muat_model()
    if model is None:
        return None
    with torch.no_grad():
        x = preprocessing(pil_image, size=model.input_size)
        probs = torch.softmax(model(x), dim=1)[0]
    sorted_idx = torch.argsort(probs, descending=True)
    top = []
    for i in sorted_idx[:n_top]:
        kode = kelas[int(i)]
        tanaman, penyakit = (kode.split("___") + ["?"])[:2]
        top.append(
            {
                "kelas": kode,
                "tanaman": tanaman.replace("_", " "),
                "penyakit": penyakit.replace("_", " "),
                "confidence": float(probs[i]),
            }
        )
    return {
        "top": top,
        "kelas": top[0]["kelas"],
        "confidence": top[0]["confidence"],
        "n_kelas": len(kelas),
    }


def grad_cam(pil_image: Image.Image, idx_kelas: int):
    """Menghitung Grad-CAM untuk kelas tertentu.

    Mengembalikan (gambar overlay PIL, peta kam numpy 0-1, persen area aktif) atau
    (None, None, None) jika model belum tersedia.
    """
    model, kelas = muat_model()
    if model is None:
        return None, None, None
    model.eval()
    layer = model.blocks[-1].point
    akt, grad = {}, {}

    def fh(_m, _i, o):
        akt["v"] = o.detach()

    def bh(_m, _gi, go):
        grad["v"] = go[0].detach()

    h1 = layer.register_forward_hook(fh)
    h2 = layer.register_full_backward_hook(bh)
    try:
        x = preprocessing(pil_image, size=model.input_size)
        logits = model(x)
        model.zero_grad()
        logits[0, idx_kelas].backward()
    finally:
        h1.remove()
        h2.remove()

    weights = grad["v"].mean(dim=(2, 3), keepdim=True)
    kam = torch.relu((weights * akt["v"]).sum(dim=1, keepdim=True)).squeeze().cpu().numpy()
    kam = (kam - kam.min()) / (kam.max() - kam.min() + 1e-8)

    pl = pil_image.convert("RGB").resize((model.input_size, model.input_size), Image.LANCZOS)
    arr = np.array(pl).astype(float)
    kam_img = np.array(
        Image.fromarray((kam * 255).astype(np.uint8)).resize(
            (model.input_size, model.input_size), Image.BILINEAR
        )
    ).astype(float) / 255.0
    kam_rgb = np.stack([kam_img * 0, kam_img, kam_img * 0], axis=2)
    overlay = 0.55 * arr + 0.45 * kam_rgb * 255
    gabungan = Image.fromarray(np.clip(overlay, 0, 255).astype(np.uint8))
    persen = float((kam > 0.5).mean() * 100)
    return gabungan, kam, persen
