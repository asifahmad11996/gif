#!/usr/bin/env python3
"""Generate FoxiGrow bot GIFs animated from banner artwork."""

from __future__ import annotations

import math
import random
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
BANNERS = ROOT / "banners"
OUT = ROOT / "gifs"

OUTPUT_SIZE = (480, 270)
FRAMES = 24
FRAME_MS = 100
FPS = 10

GOLD = (255, 210, 80)
MINT = (100, 240, 200)
WHITE = (255, 255, 255)


def cover_crop(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    target_w, target_h = size
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w, new_h = int(src_w * scale), int(src_h * scale)
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def zoom_pan_frame(
    base: Image.Image,
    size: tuple[int, int],
    scale: float,
    pan_x: float,
    pan_y: float,
) -> Image.Image:
    w, h = size
    canvas = Image.new("RGB", (w, h), (0, 0, 0))
    zoomed_w = int(w * scale)
    zoomed_h = int(h * scale)
    zoomed = base.resize((zoomed_w, zoomed_h), Image.Resampling.LANCZOS)
    max_x = zoomed_w - w
    max_y = zoomed_h - h
    left = int(max_x * (0.5 + pan_x * 0.5))
    top = int(max_y * (0.5 + pan_y * 0.5))
    left = max(0, min(left, max_x))
    top = max(0, min(top, max_y))
    canvas.paste(zoomed.crop((left, top, left + w, top + h)))
    return canvas


def sparkle_overlay(size: tuple[int, int], frame: int, total: int, seed: int, count: int = 18) -> Image.Image:
    w, h = size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    rng = random.Random(seed)

    for i in range(count):
        x = rng.randint(20, w - 20)
        y = rng.randint(20, h - 20)
        phase = (frame / total + i * 0.13) % 1.0
        alpha = int(180 * math.sin(math.pi * phase) ** 2)
        if alpha < 20:
            continue
        r = rng.randint(2, 5)
        color = GOLD if i % 3 else MINT
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(*color, alpha))
        if alpha > 100:
            draw.line((x - r * 2, y, x + r * 2, y), fill=(*WHITE, alpha // 2), width=1)
            draw.line((x, y - r * 2, x, y + r * 2), fill=(*WHITE, alpha // 2), width=1)

    return overlay


def shimmer_overlay(size: tuple[int, int], frame: int, total: int) -> Image.Image:
    w, h = size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    sweep = (frame / total) * (w + 200) - 100
    for offset in range(-40, 41, 8):
        x = sweep + offset
        alpha = max(0, 28 - abs(offset) // 2)
        draw.line((x, 0, x - 80, h), fill=(255, 255, 255, alpha), width=3)
    return overlay


def glow_pulse(img: Image.Image, strength: float) -> Image.Image:
  boosted = ImageEnhance.Brightness(img).enhance(1.0 + 0.06 * strength)
  return ImageEnhance.Contrast(boosted).enhance(1.0 + 0.04 * strength)


def animate_banner(
    banner_name: str,
    output_name: str,
    *,
    zoom_range: tuple[float, float] = (1.0, 1.08),
    pan_amp: tuple[float, float] = (0.06, 0.04),
    sparkle_count: int = 14,
    shimmer: bool = True,
    seed: int = 42,
) -> None:
    banner_path = BANNERS / banner_name
    if not banner_path.exists():
        raise FileNotFoundError(banner_path)

    base = cover_crop(Image.open(banner_path).convert("RGB"), OUTPUT_SIZE)
    frames: list[Image.Image] = []

    z0, z1 = zoom_range
    px, py = pan_amp

    for i in range(FRAMES):
        t = i / FRAMES
        wave = 0.5 - 0.5 * math.cos(2 * math.pi * t)
        scale = z0 + (z1 - z0) * wave
        pan_x = math.sin(2 * math.pi * t) * px
        pan_y = math.cos(2 * math.pi * t) * py

        frame = zoom_pan_frame(base, OUTPUT_SIZE, scale, pan_x, pan_y)
        pulse = math.sin(2 * math.pi * t) ** 2
        frame = glow_pulse(frame, pulse)

        rgba = frame.convert("RGBA")
        rgba = Image.alpha_composite(rgba, sparkle_overlay(OUTPUT_SIZE, i, FRAMES, seed, sparkle_count))
        if shimmer and i % 3 == 0:
            rgba = Image.alpha_composite(rgba, shimmer_overlay(OUTPUT_SIZE, i, FRAMES))

        frames.append(rgba.convert("RGB"))

    save_gif(frames, OUT / output_name)


def save_gif_ffmpeg(frames: list[Image.Image], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        for i, frame in enumerate(frames):
            frame.save(tmp_path / f"frame_{i:03d}.png")

        palette = tmp_path / "palette.png"
        part_a = (
            f"fps={FPS},scale={OUTPUT_SIZE[0]}:{OUTPUT_SIZE[1]}:flags=lanczos,split[s0][s1];"
            "[s0]palettegen=stats_mode=diff:max_colors=128:reserve_transparent=0[p];"
            "[s1][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle"
        )
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", str(tmp_path / "frame_%03d.png"),
            "-vf", part_a,
            "-loop", "0",
            str(path),
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    size_kb = path.stat().st_size // 1024
    print(f"  {path.name} ({len(frames)} frames, {OUTPUT_SIZE[0]}x{OUTPUT_SIZE[1]}, {size_kb}KB)")


def save_gif_pillow(frames: list[Image.Image], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sample = frames[:: max(1, len(frames) // 8)]
    combined = Image.new("RGB", (OUTPUT_SIZE[0], OUTPUT_SIZE[1] * len(sample)))
    for idx, frame in enumerate(sample):
        combined.paste(frame, (0, idx * OUTPUT_SIZE[1]))
    palette_img = combined.quantize(colors=192, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)

    quantized_frames = [
        frame.quantize(palette=palette_img, dither=Image.Dither.FLOYDSTEINBERG).convert("RGB")
        for frame in frames
    ]
    quantized_frames[0].save(
        path,
        save_all=True,
        append_images=quantized_frames[1:],
        duration=FRAME_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )


def save_gif(frames: list[Image.Image], path: Path) -> None:
    if shutil.which("ffmpeg"):
        try:
            save_gif_ffmpeg(frames, path)
            return
        except subprocess.CalledProcessError:
            pass
    save_gif_pillow(frames, path)
    size_kb = path.stat().st_size // 1024
    print(f"  {path.name} ({len(frames)} frames, {OUTPUT_SIZE[0]}x{OUTPUT_SIZE[1]}, {size_kb}KB)")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print("Generating banner-based GIFs...")

    animate_banner("task-center.png", "task-center-live.gif", seed=11)
    animate_banner("must-do-link-accounts.png", "must-do-link-accounts.gif", zoom_range=(1.0, 1.07), seed=22)
    animate_banner("high-value-20-task.png", "high-value-20-task.gif", zoom_range=(1.02, 1.10), sparkle_count=18, seed=33)
    animate_banner("drip-tasks-soon.png", "drip-tasks-soon.gif", pan_amp=(0.04, 0.06), seed=44)
    animate_banner("social-follow-earn.png", "social-follow-earn.gif", seed=55)
    animate_banner("daily-digest.png", "new-task-alert.gif", zoom_range=(1.0, 1.09), sparkle_count=16, shimmer=True, seed=66)
    animate_banner("download-register.png", "download-register.gif", seed=77)
    animate_banner("youtube-watch-update.png", "youtube-watch-update.gif", zoom_range=(1.0, 1.07), sparkle_count=12, shimmer=False, seed=88)
    animate_banner("project-activities-task-system.png", "project-activities-task-system.gif", zoom_range=(1.0, 1.06), sparkle_count=10, shimmer=False, seed=99)

    print(f"Done → {OUT}")


if __name__ == "__main__":
    main()
