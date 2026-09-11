#!/usr/bin/env python3
"""Build Digital Freedom Contest vertical video."""

from __future__ import annotations

import asyncio
import json
import math
import subprocess
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
AUDIO = ROOT / "audio"
FRAMES = ROOT / "frames"
OUTPUT = ROOT / "output"

W, H = 1080, 1920
FPS = 30
VOICE = "en-US-GuyNeural"


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in paths:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    sw, sh = img.size
    scale = max(tw / sw, th / sh)
    nw, nh = int(sw * scale), int(sh * scale)
    resized = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left, top = (nw - tw) // 2, (nh - th) // 2
    return resized.crop((left, top, left + tw, top + th))


def darken(img: Image.Image, factor: float = 0.55) -> Image.Image:
    return ImageEnhance.Brightness(img).enhance(factor)


def draw_gradient_overlay(img: Image.Image) -> Image.Image:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(img.height):
        t = y / img.height
        alpha = int(40 + 170 * (t ** 1.4))
        draw.line([(0, y), (img.width, y)], fill=(6, 10, 24, alpha))
    return Image.alpha_composite(img.convert("RGBA"), overlay)


def wrap_text(text: str, font, max_width: int) -> list[str]:
    words = text.replace("\n", " ").split()
    lines: list[str] = []
    current: list[str] = []
    draw = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    for word in words:
        trial = " ".join(current + [word])
        if draw.textlength(trial, font=font) <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def draw_centered_block(
    draw: ImageDraw.ImageDraw,
    lines: list[str],
    y_start: int,
    font,
    fill,
    stroke=0,
    stroke_fill=(0, 0, 0),
    line_gap: int = 14,
) -> int:
    heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        heights.append(bbox[3] - bbox[1])
    total_h = sum(heights) + line_gap * (len(lines) - 1)
    y = y_start
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, y), line, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        y += heights[i] + line_gap
    return y_start + total_h


def speech_player_frame(base: Image.Image) -> Image.Image:
    img = cover(base, (W, H))
    img = darken(img, 0.75)
    img = draw_gradient_overlay(img)
    draw = ImageDraw.Draw(img)

    # Player chrome
    draw.rounded_rectangle((70, 220, W - 70, H - 520), radius=28, fill=(12, 16, 28, 220), outline=(255, 150, 60, 180), width=3)
    thumb = cover(Image.open(ASSETS / "yt_sddefault.jpg").convert("RGB"), (W - 180, int((H - 760) * 0.62)))
    thumb = darken(thumb, 0.9)
    img.paste(thumb, (90, 250))

    play_r = 70
    cx, cy = W // 2, 250 + thumb.height // 2
    draw.ellipse((cx - play_r, cy - play_r, cx + play_r, cy + play_r), fill=(255, 140, 50, 220))
    draw.polygon([(cx - 18, cy - 34), (cx - 18, cy + 34), (cx + 36, cy)], fill=(255, 255, 255))

    title_font = load_font(42, bold=True)
    sub_font = load_font(28)
    small_font = load_font(24)
    draw_centered_block(draw, ["PAVEL DUROV"], 250 + thumb.height + 40, title_font, (255, 220, 120), stroke=2, stroke_fill=(0, 0, 0))
    draw_centered_block(draw, ["Oslo Freedom Forum"], 250 + thumb.height + 100, sub_font, (230, 235, 255))
    draw_centered_block(draw, ["Source: youtube.com/watch?v=1Yq_5aDdJ24"], H - 470, small_font, (160, 175, 210))
    draw_centered_block(draw, ["Communication Technology", "and the Struggle for Freedom"], H - 420, sub_font, (255, 255, 255), stroke=1, stroke_fill=(0, 0, 0))
    return img.convert("RGB")


def render_still(scene_key: str, overlay: str | None, style: str) -> Image.Image:
    if scene_key == "durov_footage":
        base = Image.open(ASSETS / "scene_speaker.jpg" if (ASSETS / "scene_speaker.jpg").exists() else ASSETS / "scene_speaker.png")
        img = speech_player_frame(base)
    else:
        path = ASSETS / f"{scene_key}.png"
        img = cover(Image.open(path).convert("RGB"), (W, H))
        img = darken(img, 0.62 if style != "hook" else 0.5)
        img = draw_gradient_overlay(img)
        draw = ImageDraw.Draw(img)

        if style == "hook":
            font = load_font(92, bold=True)
            lines = wrap_text(overlay or "", font, W - 120)
            draw_centered_block(draw, lines, H // 2 - 120, font, (255, 245, 230), stroke=4, stroke_fill=(20, 10, 0))
        elif style == "quote":
            font = load_font(54, bold=True)
            quote = overlay or ""
            lines = wrap_text(quote, font, W - 140)
            draw_centered_block(draw, lines, 760, font, (255, 255, 255), stroke=3, stroke_fill=(0, 0, 0), line_gap=18)
            draw_centered_block(draw, ["— Pavel Durov"], 1450, load_font(34), (255, 180, 80))
        elif style == "emphasis":
            font = load_font(86, bold=True)
            lines = wrap_text(overlay or "", font, W - 120)
            draw_centered_block(draw, lines, H // 2 - 80, font, (255, 120, 70), stroke=4, stroke_fill=(0, 0, 0))
        elif style == "cta":
            font = load_font(72, bold=True)
            lines = wrap_text(overlay or "", font, W - 120)
            draw_centered_block(draw, lines, H // 2 - 100, font, (120, 240, 200), stroke=3, stroke_fill=(0, 0, 0))
        elif style == "end":
            font = load_font(64, bold=True)
            lines = wrap_text(overlay or "", font, W - 120)
            draw_centered_block(draw, lines, H // 2 - 140, font, (255, 200, 80), stroke=3, stroke_fill=(0, 0, 0))
            draw_centered_block(draw, ["#DigitalFreedom", "t.me/FoxiGrowbot"], H // 2 + 80, load_font(40), (255, 255, 255))
        elif overlay:
            font = load_font(48, bold=True)
            lines = wrap_text(overlay, font, W - 120)
            draw_centered_block(draw, lines, 820, font, (240, 245, 255), stroke=2, stroke_fill=(0, 0, 0))
        img = img.convert("RGB")
    return img


def ken_burns_frames(still: Image.Image, duration: float, zoom: float = 1.08) -> list[Image.Image]:
    total = max(1, int(duration * FPS))
    frames: list[Image.Image] = []
    base = still.resize((int(W * zoom), int(H * zoom)), Image.Resampling.LANCZOS)
    bw, bh = base.size
    for i in range(total):
        t = i / max(total - 1, 1)
        left = int((bw - W) * t * 0.5)
        top = int((bh - H) * t * 0.35)
        frame = base.crop((left, top, left + W, top + H))
        frames.append(frame)
    return frames


SEGMENTS = [
    {
        "id": "01_hook",
        "text": "The ship is already sinking.",
        "scene": "scene_titanic",
        "overlay": "The ship is already sinking.",
        "style": "hook",
    },
    {
        "id": "02_intro",
        "text": "Pavel Durov at the Oslo Freedom Forum:",
        "scene": "durov_footage",
        "overlay": None,
        "style": "speech",
    },
    {
        "id": "03_quote1",
        "text": "Our personal freedoms have been eroded everywhere in the world, almost without exception.",
        "scene": "durov_footage",
        "overlay": "Our personal freedoms have been eroded everywhere in the world — almost without exception.",
        "style": "quote",
    },
    {
        "id": "04_titanic",
        "text": "He compared it to the Titanic. People refused to leave for two hours after the iceberg hit.",
        "scene": "scene_titanic",
        "overlay": "Like the Titanic — we refuse to see the danger.",
        "style": "normal",
    },
    {
        "id": "05_surveillance",
        "text": "Governments now ask you to give up privacy for safety.",
        "scene": "scene_surveillance",
        "overlay": "Give up privacy… for safety?",
        "style": "normal",
    },
    {
        "id": "06_scam",
        "text": "This deal is always a scam.",
        "scene": "scene_freedom",
        "overlay": "This deal is always a scam.",
        "style": "emphasis",
    },
    {
        "id": "07_telegram",
        "text": "Russia banned Telegram for refusing mass surveillance. Yet ninety five percent of Russian teenagers still use it every month.",
        "scene": "scene_freedom",
        "overlay": "95% still use Telegram every month",
        "style": "normal",
    },
    {
        "id": "08_west",
        "text": "If the ship of Western freedom sinks, the rest of the world will follow.",
        "scene": "scene_speaker",
        "overlay": "If Western freedom sinks,\nthe world will follow.",
        "style": "quote",
    },
    {
        "id": "09_backup",
        "text": "We don't get a backup civilization.",
        "scene": "scene_titanic",
        "overlay": "There is no backup civilization.",
        "style": "cta",
    },
    {
        "id": "10_fix",
        "text": "Fix the ship. Defend digital freedom.",
        "scene": "scene_freedom",
        "overlay": "Fix the ship.\nDefend digital freedom.",
        "style": "cta",
    },
    {
        "id": "11_end",
        "text": "Digital Freedom Contest. Join the fight at FoxiGrow.",
        "scene": "scene_freedom",
        "overlay": "Digital Freedom Contest",
        "style": "end",
    },
]


async def synthesize_all() -> list[dict]:
    import edge_tts

    AUDIO.mkdir(parents=True, exist_ok=True)
    meta: list[dict] = []
    for seg in SEGMENTS:
        out = AUDIO / f"{seg['id']}.mp3"
        communicate = edge_tts.Communicate(seg["text"], VOICE, rate="-4%", pitch="+0Hz")
        await communicate.save(str(out))
        probe = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(out)],
            capture_output=True,
            text=True,
            check=True,
        )
        duration = float(json.loads(probe.stdout)["format"]["duration"])
        seg_meta = {**seg, "audio": str(out), "duration": duration}
        meta.append(seg_meta)
        print(f"  audio {seg['id']}: {duration:.1f}s")
    return meta


def write_segment_videos(meta: list[dict]) -> list[Path]:
    FRAMES.mkdir(parents=True, exist_ok=True)
    seg_videos: list[Path] = []
    for seg in meta:
        still = render_still(seg["scene"], seg.get("overlay"), seg["style"])
        frames = ken_burns_frames(still, seg["duration"] + 0.15)
        seg_dir = FRAMES / seg["id"]
        seg_dir.mkdir(parents=True, exist_ok=True)
        for i, frame in enumerate(frames):
            frame.save(seg_dir / f"frame_{i:04d}.png")

        silent = OUTPUT / f"{seg['id']}_silent.mp4"
        run([
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", str(seg_dir / "frame_%04d.png"),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            str(silent),
        ])

        final = OUTPUT / f"{seg['id']}.mp4"
        run([
            "ffmpeg", "-y",
            "-i", str(silent),
            "-i", seg["audio"],
            "-c:v", "copy", "-c:a", "aac", "-shortest",
            str(final),
        ])
        seg_videos.append(final)
        print(f"  video {seg['id']}")
    return seg_videos


def make_music(duration: float, path: Path) -> None:
    # Cinematic ambient pad under narration
    run([
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"anoisesrc=color=brown:amplitude=0.015:duration={duration}",
        "-f", "lavfi", "-i", f"sine=frequency=55:duration={duration}",
        "-f", "lavfi", "-i", f"sine=frequency=82.41:duration={duration}",
        "-filter_complex",
        "[0][1][2]amix=inputs=3:duration=first,volume=0.35,afade=t=in:st=0:d=2,afade=t=out:st="
        f"{max(0, duration - 3)}:d=3,lowpass=f=500",
        "-c:a", "aac", str(path),
    ])


def concat_videos(seg_videos: list[Path], music: Path, out: Path) -> None:
    concat_list = OUTPUT / "concat.txt"
    concat_list.write_text("\n".join(f"file '{p.name}'" for p in seg_videos))
    merged = OUTPUT / "merged_no_music.mp4"
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
        "-c", "copy", str(merged),
    ])
    run([
        "ffmpeg", "-y",
        "-i", str(merged),
        "-i", str(music),
        "-filter_complex", "[1:a]volume=0.22[m];[0:a][m]amix=inputs=2:duration=first:dropout_transition=2[aout]",
        "-map", "0:v", "-map", "[aout]",
        "-c:v", "copy", "-c:a", "aac",
        str(out),
    ])


def export_horizontal(vertical: Path, out: Path) -> None:
    run([
        "ffmpeg", "-y", "-i", str(vertical),
        "-vf", "scale=-2:1080,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black",
        "-c:v", "libx264", "-c:a", "aac",
        str(out),
    ])


async def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    print("Synthesizing voiceover...")
    meta = await synthesize_all()
    total = sum(s["duration"] for s in meta) + 0.5
    print("Rendering segments...")
    seg_videos = write_segment_videos(meta)
    print("Adding music...")
    music = OUTPUT / "music.m4a"
    make_music(total, music)
    vertical = OUTPUT / "digital-freedom-contest-vertical.mp4"
    print("Merging final video...")
    concat_videos(seg_videos, music, vertical)
    horizontal = OUTPUT / "digital-freedom-contest-horizontal.mp4"
    export_horizontal(vertical, horizontal)
    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(vertical)],
        capture_output=True,
        text=True,
        check=True,
    )
    info = json.loads(probe.stdout)
    dur = float(info["format"]["duration"])
    print(f"DONE\n  Vertical:   {vertical}\n  Horizontal: {horizontal}\n  Duration:   {dur:.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
