"""Pengujian alur teknis PlantVision AI dengan citra sintetis kecil."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest
import torch
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.model import ModelKlasifikasiDaun, jumlah_param  # noqa: E402
from src.training import (  # noqa: E402
    grad_cam,
    hitung_metrik,
    muat_model,
    prediksi,
    preprocessing,
)

MODEL_PATH = ROOT / "models" / "model_cnn.pt"


def _dummy_image(color: tuple = (60, 140, 60), size: int = 160) -> Image.Image:
    arr = np.zeros((size, size, 3), dtype=np.uint8)
    arr[:, :] = color
    return Image.fromarray(arr)


def test_model_forward_shape() -> None:
    model = ModelKlasifikasiDaun(n_kelas=5)
    out = model(torch.randn(2, 3, 128, 128))
    assert out.shape == (2, 5)


def test_model_param_count_small() -> None:
    model = ModelKlasifikasiDaun(n_kelas=38)
    assert 100_000 < jumlah_param(model) < 1_000_000


def test_preprocessing_normalization() -> None:
    tensor = preprocessing(_dummy_image())
    assert tensor.shape == (1, 3, 128, 128)
    assert torch.isfinite(tensor).all()


def test_confusion_metrics_perfect() -> None:
    mat = np.diag([5, 5, 5])
    metrik = hitung_metrik(mat)
    assert metrik["accuracy"] == 1.0
    assert metrik["f1_macro"] == 1.0


def test_confusion_metrics_imperfect() -> None:
    mat = np.array([[8, 2], [1, 9]])
    metrik = hitung_metrik(mat)
    assert 0.0 < metrik["accuracy"] < 1.0
    assert 0.0 < metrik["recall_macro"] <= 1.0


pytestmark = pytest.mark.filterwarnings("ignore")


def test_dataloaders_missing_raises(tmp_path: Path, monkeypatch) -> None:
    from src import training

    monkeypatch.setattr(training, "DATASET_DIR", tmp_path / "tidak-ada")
    with pytest.raises(FileNotFoundError):
        training.build_loaders()


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="Model belum dilatih")
def test_predict_with_trained_model() -> None:
    result = prediksi(_dummy_image())
    assert result is not None
    assert result["kelas"] in result["top"][0]["kelas"]
    assert 0.0 <= result["confidence"] <= 1.0
    assert len(result["top"]) <= 3


@pytest.mark.skipif(not MODEL_PATH.exists(), reason="Model belum dilatih")
def test_grad_cam_shapes() -> None:
    _, kelas = muat_model()
    overlay, kam, persen = grad_cam(_dummy_image(), 0)
    assert overlay is not None
    assert kam.shape[0] > 0
    assert 0.0 <= persen <= 100.0
