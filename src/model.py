"""Arsitektur CNN ringan untuk klasifikasi penyakit daun (Sesi 2).

Model: depthwise-separable CNN menyerupai MobileNet kecil.
Input: citra RGB 128x128 (ternormalisasi ImageNet).
Output: logits untuk sejumlah kelas daun.

Arsitektur ini ringan (~200 ribu parameter) sehingga dapat dilatih di CPU.
"""

from __future__ import annotations

import torch
import torch.nn as nn

IMG_SIZE = 128
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


class BlokDepthwiseSeparable(nn.Module):
    """Blok depthwise separable: Dwise3x3 -> BN -> ReLU6 -> Pointwise1x1 -> BN -> ReLU6."""

    def __init__(self, c_in: int, c_out: int, stride: int = 1):
        super().__init__()
        self.depth = nn.Conv2d(
            c_in, c_in, kernel_size=3, stride=stride, padding=1, groups=c_in, bias=False
        )
        self.bn1 = nn.BatchNorm2d(c_in)
        self.point = nn.Conv2d(c_in, c_out, kernel_size=1, bias=False)
        self.bn2 = nn.BatchNorm2d(c_out)
        self.re = nn.ReLU6(inplace=True)
        self.residual = stride == 1 and c_in == c_out

    def forward(self, x):
        residual = x if self.residual else 0
        x = self.re(self.bn1(self.depth(x)))
        x = self.re(self.bn2(self.point(x)))
        return x + residual if self.residual else x


class ModelKlasifikasiDaun(nn.Module):
    """CNN ringan untuk klasifikasi daun."""

    def __init__(self, n_kelas: int, input_size: int = IMG_SIZE):
        super().__init__()
        self.input_size = input_size
        self.prep = nn.Sequential(
            nn.Conv2d(3, 32, 3, 1, 1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU6(inplace=True),
        )
        self.blocks = nn.Sequential(
            BlokDepthwiseSeparable(32, 64, stride=2),
            BlokDepthwiseSeparable(64, 128, stride=2),
            BlokDepthwiseSeparable(128, 256, stride=2),
            BlokDepthwiseSeparable(256, 512, stride=2),
        )
        self.gap = nn.AdaptiveAvgPool2d(1)
        self.head = nn.Sequential(nn.Dropout(0.2), nn.Linear(512, n_kelas))

    def forward(self, x):
        x = self.prep(x)
        x = self.blocks(x)
        x = self.gap(x).flatten(1)
        return self.head(x)


def jumlah_param(model: nn.Module) -> int:
    """Menghitung jumlah parameter yang dapat dilatih."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)
