#!/usr/bin/env python3
"""Resize high-quality FoxiGrow 1536 banners to mini-app sizes."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
BANNERS = ROOT / "banners"


def hero_strip(src: Path, dst: Path, size: tuple[int, int], top_frac: float = 0.36) -> None:
    tw, th = size
    im = Image.open(src).convert("RGB")
    w, h = im.size
    crop = im.crop((0, 0, w, int(h * top_frac)))
    cw, ch = crop.size
    ratio = tw / th
    if cw / ch > ratio:
        nw = int(ch * ratio)
        crop = crop.crop(((cw - nw) // 2, 0, (cw + nw) // 2, ch))
    else:
        nh = int(cw / ratio)
        crop = crop.crop((0, 0, cw, nh))
    out = crop.resize(size, Image.Resampling.LANCZOS)
    out = out.filter(ImageFilter.UnsharpMask(radius=0.8, percent=140, threshold=1))
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.save(dst, "PNG", optimize=True)


def main() -> None:
    strips_320 = [
        (BANNERS / "foxigroworderbot-api-partners.png", BANNERS / "320x50" / "foxigrow-resell-320x50.png"),
        (BANNERS / "foxigroworderbot-launch.png", BANNERS / "320x50" / "foxigrow-orderbot-320x50.png"),
        (BANNERS / "action-persistence-income.png", BANNERS / "320x50" / "foxigrow-earn-320x50.png"),
    ]
    for src, dst in strips_320:
        hero_strip(src, dst, (320, 50))

    strips_400 = [
        (BANNERS / "foxigroworderbot-api-partners.png", BANNERS / "1200x400" / "foxigrow-resell-1200x400.png"),
        (BANNERS / "foxigroworderbot-api-partners.png", BANNERS / "1200x400" / "foxigrow-partner-api-1200x400.png"),
        (BANNERS / "foxigroworderbot-launch.png", BANNERS / "1200x400" / "foxigrow-orderbot-1200x400.png"),
        (BANNERS / "action-persistence-income.png", BANNERS / "1200x400" / "foxigrow-earn-usdt-1200x400.png"),
    ]
    for src, dst in strips_400:
        hero_strip(src, dst, (1200, 400), top_frac=0.40)

    print("Done. Note: add partner-api source PNG if distinct from resell.")


if __name__ == "__main__":
    main()
