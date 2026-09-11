#!/usr/bin/env python3
"""Resize FoxiGrow theme master banners to mini-app sizes.

Master artwork lives in banners/masters/ (1536px FoxiGrow theme).
Run after replacing master PNGs.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MASTERS = ROOT / "banners" / "masters"
OUT320 = ROOT / "banners" / "320x50"
OUT400 = ROOT / "banners" / "1200x400"


def orange_score(band: np.ndarray) -> float:
    r, g, b = band[:, :, 0].astype(float), band[:, :, 1].astype(float), band[:, :, 2].astype(float)
    orange = (r > 140) & (g > 80) & (g < 200) & (b < 120)
    navy = (r < 60) & (g < 80) & (b > 40)
    return float(orange.mean() * 2 + navy.mean())


def find_best_top(arr: np.ndarray, band_frac: float = 0.22) -> tuple[int, int]:
    h = arr.shape[0]
    band_h = max(80, int(h * band_frac))
    best_score, best_top = 0.0, 0
    for top in range(0, h - band_h, 6):
        score = orange_score(arr[top : top + band_h])
        if score > best_score:
            best_score, best_top = score, top
    return best_top, band_h


def fit_cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    w, h = img.size
    scale = max(tw / w, th / h)
    nw, nh = int(w * scale), int(h * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left, top = (nw - tw) // 2, (nh - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def polish(img: Image.Image) -> Image.Image:
    img = img.filter(ImageFilter.UnsharpMask(radius=1.0, percent=150, threshold=1))
    return ImageEnhance.Contrast(img).enhance(1.06)


def strip_320(src: Path, dst: Path) -> None:
    arr = np.array(Image.open(src).convert("RGB"))
    top, band_h = find_best_top(arr)
    crop = Image.fromarray(arr).crop((0, top, arr.shape[1], top + band_h))
    polish(fit_cover(crop, (320, 50))).save(dst, "PNG", optimize=True)


def hero_400(src: Path, dst: Path) -> None:
    im = Image.open(src).convert("RGB")
    w, h = im.size
    crop = im.crop((0, 0, w, int(h * 0.45)))
    polish(fit_cover(crop, (1200, 400))).save(dst, "PNG", optimize=True)


def main() -> None:
    OUT320.mkdir(parents=True, exist_ok=True)
    OUT400.mkdir(parents=True, exist_ok=True)

    for src, dst in [
        ("foxigrow-theme-resell-wide.png", "foxigrow-resell-320x50.png"),
        ("foxigrow-theme-api-wide.png", "foxigrow-partner-api-320x50.png"),
        ("foxigrow-theme-orderbot-wide.png", "foxigrow-orderbot-320x50.png"),
        ("foxigrow-theme-earn-wide.png", "foxigrow-earn-320x50.png"),
    ]:
        strip_320(MASTERS / src, OUT320 / dst)
        print(f"320x50 {dst}")

    for src, dst in [
        ("foxigrow-theme-resell-1200x400.png", "foxigrow-resell-1200x400.png"),
        ("foxigrow-theme-api-1200x400.png", "foxigrow-partner-api-1200x400.png"),
        ("foxigrow-theme-orderbot-1200x400.png", "foxigrow-orderbot-1200x400.png"),
        ("foxigrow-theme-earn-1200x400.png", "foxigrow-earn-usdt-1200x400.png"),
    ]:
        hero_400(MASTERS / src, OUT400 / dst)
        print(f"1200x400 {dst}")


if __name__ == "__main__":
    main()
