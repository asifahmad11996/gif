#!/usr/bin/env python3
"""Generate FoxiGrow bot push notification GIFs."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "gifs"

# FoxiGrow brand palette
BG_TOP = (18, 24, 42)
BG_BOTTOM = (10, 14, 28)
ORANGE = (255, 140, 50)
GOLD = (255, 200, 80)
WHITE = (245, 247, 255)
MINT = (72, 220, 180)
PINK = (255, 110, 150)


def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)


def gradient_bg(size: tuple[int, int], frame: int, total: int) -> Image.Image:
    w, h = size
    pulse = 0.5 + 0.5 * math.sin(2 * math.pi * frame / total)
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / max(h - 1, 1)
        r = lerp(BG_TOP[0], BG_BOTTOM[0], t)
        g = lerp(BG_TOP[1], BG_BOTTOM[1], t)
        b = lerp(BG_TOP[2], BG_BOTTOM[2], t)
        glow = int(12 * pulse * (1 - abs(t - 0.35) * 2))
        draw.line([(0, y), (w, y)], fill=(r + glow, g + glow // 2, b))
    return img


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_fox_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float = 1.0) -> None:
    s = scale
    # Ears
    draw.polygon(
        [(cx - 34 * s, cy - 30 * s), (cx - 18 * s, cy - 62 * s), (cx - 2 * s, cy - 28 * s)],
        fill=ORANGE,
    )
    draw.polygon(
        [(cx + 2 * s, cy - 28 * s), (cx + 18 * s, cy - 62 * s), (cx + 34 * s, cy - 30 * s)],
        fill=ORANGE,
    )
    # Head
    draw.ellipse((cx - 42 * s, cy - 34 * s, cx + 42 * s, cy + 38 * s), fill=ORANGE)
    draw.ellipse((cx - 30 * s, cy - 10 * s, cx + 30 * s, cy + 34 * s), fill=(255, 220, 185))
    # Eyes
    draw.ellipse((cx - 22 * s, cy - 8 * s, cx - 8 * s, cy + 6 * s), fill=WHITE)
    draw.ellipse((cx + 8 * s, cy - 8 * s, cx + 22 * s, cy + 6 * s), fill=WHITE)
    draw.ellipse((cx - 16 * s, cy - 2 * s, cx - 10 * s, cy + 4 * s), fill=(30, 30, 40))
    draw.ellipse((cx + 10 * s, cy - 2 * s, cx + 16 * s, cy + 4 * s), fill=(30, 30, 40))
    # Nose
    draw.ellipse((cx - 6 * s, cy + 8 * s, cx + 6 * s, cy + 18 * s), fill=(50, 35, 30))


def draw_coin(draw: ImageDraw.ImageDraw, x: int, y: int, r: int, label: str = "$") -> None:
    draw.ellipse((x - r, y - r, x + r, y + r), fill=GOLD, outline=(220, 170, 40), width=2)
    font = load_font(max(12, r), bold=True)
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x - tw // 2, y - th // 2 - 1), label, fill=(120, 70, 10), font=font)


def centered_text(draw: ImageDraw.ImageDraw, y: int, text: str, font, fill, width: int) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) // 2, y), text, fill=fill, font=font)


def save_gif(frames: list[Image.Image], path: Path, duration: int = 90) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        optimize=True,
        disposal=2,
    )


def make_task_center_gif() -> None:
    w, h = 480, 270
    total = 24
    frames = []
    title_font = load_font(34, bold=True)
    sub_font = load_font(18)
    badge_font = load_font(16, bold=True)

    for i in range(total):
        img = gradient_bg((w, h), i, total)
        draw = ImageDraw.Draw(img)
        bounce = math.sin(2 * math.pi * i / total) * 6
        draw_fox_icon(draw, 95, int(128 + bounce), 0.95)

        centered_text(draw, 34, "TASK CENTER", title_font, WHITE, w)
        centered_text(draw, 78, "21 Tasks Available", sub_font, MINT, w)
        centered_text(draw, 104, "Earn USDT + FG", sub_font, GOLD, w)

        pulse = 0.85 + 0.15 * math.sin(2 * math.pi * i / total)
        bw, bh = int(170 * pulse), 42
        bx, by = w - bw - 24, 190
        draw.rounded_rectangle((bx, by, bx + bw, by + bh), radius=12, fill=ORANGE)
        centered_text(draw, by + 10, "OPEN TASKS", badge_font, WHITE, w)

        for j, (cx, cy) in enumerate([(300, 58), (360, 92), (410, 140)]):
            phase = i / total + j * 0.2
            oy = int(math.sin(2 * math.pi * phase) * 8)
            draw_coin(draw, cx, cy + oy, 16, "FG")

        frames.append(img)
    save_gif(frames, OUT / "task-center-live.gif")


def make_must_do_gif() -> None:
    w, h = 480, 270
    total = 20
    frames = []
    title_font = load_font(30, bold=True)
    sub_font = load_font(17)
    plat_font = load_font(14, bold=True)
    platforms = ["X", "TT", "IG", "YT", "FB"]

    for i in range(total):
        img = gradient_bg((w, h), i, total)
        draw = ImageDraw.Draw(img)
        draw_fox_icon(draw, 88, 122, 0.85)
        centered_text(draw, 24, "MUST DO", title_font, GOLD, w)
        centered_text(draw, 58, "Link Your Accounts", sub_font, WHITE, w)
        centered_text(draw, 84, "+10 FG  (+$0.10)", sub_font, MINT, w)

        start_x = 190
        for j, p in enumerate(platforms):
            flash = (i + j * 2) % 10 < 5
            color = ORANGE if flash else (255, 170, 100)
            x = start_x + j * 52
            draw.rounded_rectangle((x, 168, x + 44, 206), radius=8, fill=color)
            bbox = draw.textbbox((0, 0), p, font=plat_font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text((x + (44 - tw) // 2, 178), p, fill=WHITE, font=plat_font)

        blink = i % 16 < 8
        if blink:
            centered_text(draw, 224, "Unlock all tasks now", sub_font, GOLD, w)

        frames.append(img)
    save_gif(frames, OUT / "must-do-link-accounts.gif", duration=110)


def make_high_value_gif() -> None:
    w, h = 480, 270
    total = 22
    frames = []
    title_font = load_font(40, bold=True)
    sub_font = load_font(18)
    note_font = load_font(15)

    for i in range(total):
        img = gradient_bg((w, h), i, total)
        draw = ImageDraw.Draw(img)
        shake = math.sin(2 * math.pi * i / total) * 3
        draw_fox_icon(draw, 400, int(118 + shake), 0.8)

        glow = int(20 + 15 * math.sin(2 * math.pi * i / total))
        centered_text(draw, 36, "$20 TASK", title_font, (255, 210 + glow // 3, 90), w)
        centered_text(draw, 88, "Reward: +110 FG", sub_font, WHITE, w)
        centered_text(draw, 114, "Paid in 2 parts: $11 + $9", note_font, MINT, w)

        for j in range(5):
            t = (i / total + j * 0.15) % 1.0
            cx = int(40 + t * 300)
            cy = int(170 + math.sin(t * 6.28) * 18)
            draw_coin(draw, cx, cy, 14, "$")

        draw.rounded_rectangle((24, 196, 220, 238), radius=10, fill=(40, 55, 90))
        draw.text((36, 206), "Task #11630", fill=GOLD, font=sub_font)

        frames.append(img)
    save_gif(frames, OUT / "high-value-20-task.gif", duration=95)


def make_drip_gif() -> None:
    w, h = 480, 270
    total = 24
    frames = []
    title_font = load_font(28, bold=True)
    sub_font = load_font(18)

    for i in range(total):
        img = gradient_bg((w, h), i, total)
        draw = ImageDraw.Draw(img)
        draw_fox_icon(draw, 110, 120, 0.9)
        centered_text(draw, 28, "DRIP TASKS", title_font, MINT, w)
        centered_text(draw, 62, "3 releasing soon", sub_font, WHITE, w)

        # Hourglass
        hx, hy = 330, 118
        draw.polygon([(hx, hy - 34), (hx + 56, hy - 34), (hx + 28, hy)], fill=(90, 110, 150))
        draw.polygon([(hx, hy + 34), (hx + 56, hy + 34), (hx + 28, hy)], fill=(90, 110, 150))
        fill_h = int(18 + 10 * math.sin(2 * math.pi * i / total))
        draw.rectangle((hx + 22, hy, hx + 34, hy + fill_h), fill=MINT)

        for j in range(3):
            t = (i / total + j * 0.33) % 1.0
            drop_y = int(150 + t * 70)
            alpha = int(255 * (1 - t))
            color = (lerp(MINT[0], BG_BOTTOM[0], t), lerp(MINT[1], BG_BOTTOM[1], t), lerp(MINT[2], BG_BOTTOM[2], t))
            draw.ellipse((300 + j * 28, drop_y, 312 + j * 28, drop_y + 12), fill=color)

        centered_text(draw, 220, "Stay ready — limited slots", sub_font, GOLD, w)
        frames.append(img)
    save_gif(frames, OUT / "drip-tasks-soon.gif")


def make_new_task_alert_gif() -> None:
    w, h = 480, 270
    total = 16
    frames = []
    title_font = load_font(30, bold=True)
    sub_font = load_font(17)

    for i in range(total):
        img = gradient_bg((w, h), i, total)
        draw = ImageDraw.Draw(img)
        pulse = 0.9 + 0.1 * math.sin(2 * math.pi * i / total)
        r = int(34 * pulse)
        draw.ellipse((w // 2 - r, 24, w // 2 + r, 24 + 2 * r), fill=PINK)
        centered_text(draw, 34, "!", load_font(28, bold=True), WHITE, w)

        draw_fox_icon(draw, w // 2, 132, 1.0)
        centered_text(draw, 196, "NEW TASK ALERT", title_font, WHITE, w)
        centered_text(draw, 228, "Tap Tasks to claim rewards", sub_font, GOLD, w)
        frames.append(img)
    save_gif(frames, OUT / "new-task-alert.gif", duration=100)


def make_social_follow_gif() -> None:
    w, h = 480, 270
    total = 20
    frames = []
    title_font = load_font(30, bold=True)
    sub_font = load_font(16)
    tags = ["Follow X", "Follow TikTok", "Subscribe YT", "Share FB"]

    for i in range(total):
        img = gradient_bg((w, h), i, total)
        draw = ImageDraw.Draw(img)
        draw_fox_icon(draw, 92, 122, 0.85)
        centered_text(draw, 24, "FOLLOW & EARN", title_font, ORANGE, w)
        idx = i % len(tags)
        centered_text(draw, 58, tags[idx], sub_font, WHITE, w)
        centered_text(draw, 82, "Up to +$0.044 per task", sub_font, MINT, w)

        for j in range(4):
            angle = 2 * math.pi * (j / 4 + i / total)
            cx = 330 + int(math.cos(angle) * 58)
            cy = 130 + int(math.sin(angle) * 38)
            draw_coin(draw, cx, cy, 15, "FG")

        frames.append(img)
    save_gif(frames, OUT / "social-follow-earn.gif")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    make_task_center_gif()
    make_must_do_gif()
    make_high_value_gif()
    make_drip_gif()
    make_new_task_alert_gif()
    make_social_follow_gif()
    print(f"Generated GIFs in {OUT}")


if __name__ == "__main__":
    main()
