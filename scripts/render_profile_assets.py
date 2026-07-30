from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "sachin-portrait.png"

BG = "#050807"
GREEN = "#00ff88"
TEAL = "#00d9c0"
CYAN = "#11d9ff"
MUTED = "#82a89a"
DIM = "#536b63"
TEXT = "#e6fff4"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        Path("C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def fitted_portrait(size: int) -> Image.Image:
    source = Image.open(SOURCE).convert("RGB")
    return source.resize((size, size), Image.Resampling.LANCZOS)


def grid(draw: ImageDraw.ImageDraw, width: int, height: int, step: int = 28) -> None:
    color = (0, 255, 136, 11)
    for x in range(0, width, step):
        draw.line((x, 0, x, height), fill=color)
    for y in range(0, height, step):
        draw.line((0, y, width, y), fill=color)


def glow_layer(size: tuple[int, int], primitives) -> Image.Image:
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    primitives(draw)
    return layer.filter(ImageFilter.GaussianBlur(5))


def paste_circle(canvas: Image.Image, portrait: Image.Image, center: tuple[int, int], radius: int) -> None:
    diameter = radius * 2
    if portrait.size != (diameter, diameter):
        portrait = portrait.resize((diameter, diameter), Image.Resampling.LANCZOS)
    mask = Image.new("L", (diameter, diameter), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, diameter - 1, diameter - 1), fill=255)
    canvas.paste(portrait, (center[0] - radius, center[1] - radius), mask)


def animated_ring(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], angle: float, color: str, width: int) -> None:
    for offset in (0, 54, 119, 208, 284):
        start = angle + offset
        draw.arc(box, start=start, end=start + 29, fill=color, width=width)
    cx = (box[0] + box[2]) / 2
    cy = (box[1] + box[3]) / 2
    radius = (box[2] - box[0]) / 2
    marker_angle = math.radians(angle + 18)
    mx = cx + math.cos(marker_angle) * radius
    my = cy + math.sin(marker_angle) * radius
    draw.ellipse((mx - 4, my - 4, mx + 4, my + 4), fill=CYAN)


def scanner(canvas: Image.Image, center: tuple[int, int], radius: int, phase: float) -> None:
    if phase < 0.12 or phase > 0.78:
        return
    progress = (phase - 0.12) / 0.66
    y = int(center[1] - radius + progress * radius * 2)
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for offset in range(-16, 17):
        alpha = max(0, 52 - abs(offset) * 3)
        draw.line(
            (center[0] - radius + 8, y + offset, center[0] + radius - 8, y + offset),
            fill=(0, 255, 136, alpha),
        )
    draw.line((center[0] - radius + 8, y, center[0] + radius - 8, y), fill=GREEN, width=2)
    canvas.paste(overlay, (0, 0), overlay)


def corners(draw: ImageDraw.ImageDraw, center: tuple[int, int], radius: int, alpha: int) -> None:
    c = (0, 255, 136, alpha)
    x1, y1 = center[0] - radius, center[1] - radius
    x2, y2 = center[0] + radius, center[1] + radius
    length = 29
    for points in (
        ((x1, y1 + length), (x1, y1), (x1 + length, y1)),
        ((x2 - length, y1), (x2, y1), (x2, y1 + length)),
        ((x1, y2 - length), (x1, y2), (x1 + length, y2)),
        ((x2 - length, y2), (x2, y2), (x2, y2 - length)),
    ):
        draw.line(points, fill=c, width=3, joint="curve")


def save_webp(frames: list[Image.Image], path: Path, duration: int) -> None:
    frames[0].save(
        path,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        quality=88,
        method=4,
        minimize_size=True,
        allow_mixed=True,
    )


def render_header() -> None:
    width, height = 1000, 566
    frames: list[Image.Image] = []
    portrait = fitted_portrait(344)
    center = (245, 280)
    radius = 172
    body_font = font(13)
    small_font = font(10)
    title_font = font(43, bold=True)
    subtitle_font = font(28, bold=True)
    label_font = font(12, bold=True)

    for index in range(36):
        phase = index / 36
        canvas = Image.new("RGB", (width, height), BG)
        draw = ImageDraw.Draw(canvas, "RGBA")
        grid(draw, width, height)
        draw.rounded_rectangle((2, 2, width - 3, height - 3), radius=18, outline=(0, 255, 136, 140), width=3)
        draw.line((18, 62, width - 18, 62), fill=(0, 255, 136, 36), width=1)
        draw.text((28, 25), "sachin@kali:~$ ./initialize_profile.sh", font=small_font, fill=MUTED)
        draw.text((854, 25), "SECURE_NODE_07", font=small_font, fill=MUTED)
        pulse = int(120 + 135 * (0.5 + 0.5 * math.sin(phase * math.tau * 2)))
        draw.ellipse((963, 27, 973, 37), fill=(0, 255, 136, pulse))

        paste_circle(canvas, portrait, center, radius)
        scan_phase = (phase * 1.35) % 1
        scanner(canvas, center, radius, scan_phase)

        ring_box = (center[0] - 190, center[1] - 190, center[0] + 190, center[1] + 190)
        ring2_box = (center[0] - 203, center[1] - 203, center[0] + 203, center[1] + 203)
        glow = glow_layer((width, height), lambda g: g.ellipse(
            (center[0] - 176, center[1] - 176, center[0] + 176, center[1] + 176),
            outline=(0, 255, 136, 180),
            width=4,
        ))
        canvas.paste(glow, (0, 0), glow)
        draw = ImageDraw.Draw(canvas, "RGBA")
        draw.ellipse((center[0] - 176, center[1] - 176, center[0] + 176, center[1] + 176), outline=GREEN, width=3)
        animated_ring(draw, ring_box, phase * 360, TEAL, 2)
        animated_ring(draw, ring2_box, -phase * 360 * 1.35, CYAN, 1)
        corners(draw, center, 155, pulse)
        draw.text((33, 133), "WEB", font=small_font, fill=TEAL)
        draw.text((29, 424), "OSINT", font=small_font, fill=TEAL)
        draw.text((435, 133), "VAPT", font=small_font, fill=TEAL)
        draw.text((442, 424), "NET", font=small_font, fill=TEAL)
        draw.text((245, 494), "BIOMETRIC MATCH // 100.00%", anchor="mm", font=small_font, fill=MUTED)
        draw.text((245, 519), "IDENTITY VERIFIED", anchor="mm", font=label_font, fill=GREEN)

        tx = 495
        draw.text((tx, 113), "IDENTITY // AUTHORIZED OPERATOR", font=small_font, fill=TEAL)
        title_x = tx + (2 if index in (32, 33) else 0)
        draw.text((title_x, 151), "SACHIN", font=title_font, fill=TEXT)
        draw.text((title_x, 199), "// CYBERSEC", font=subtitle_font, fill=GREEN)
        draw.line((tx, 244, 948, 244), fill=(0, 255, 136, 90), width=1)
        draw.text((tx, 263), "ETHICAL HACKER • SECURITY RESEARCHER", font=small_font, fill="#b9d8cc")
        draw.text((tx, 286), "PENETRATION TESTER • TRAINER • BUG HUNTER", font=small_font, fill="#b9d8cc")

        boot = [
            "> Loading security modules",
            "> Initializing reconnaissance engine",
            "> Mounting OWASP knowledge base",
            "> Verifying operator identity",
        ]
        for line_index, line in enumerate(boot):
            visible = (index - line_index * 3) % 36 > 2
            color = MUTED if visible else "#22372f"
            y = 335 + line_index * 39
            draw.text((tx, y), line, font=body_font, fill=color)
            draw.text((918, y), "[OK]" if visible else "[--]", font=body_font, fill=GREEN if visible else DIM)

        draw.rounded_rectangle((tx, 493, 950, 544), radius=8, fill=(0, 255, 136, 10), outline=(0, 255, 136, 72), width=1)
        draw.ellipse((511, 514, 521, 524), fill=(0, 255, 136, pulse))
        draw.text((530, 508), "ONLINE // ACCESS GRANTED", font=label_font, fill=GREEN)
        if index % 10 < 6:
            draw.rectangle((921, 507, 929, 529), fill=GREEN)

        frames.append(canvas)

    save_webp(frames, ASSETS / "cyber-header.webp", 100)


def render_avatar() -> None:
    width = height = 520
    frames: list[Image.Image] = []
    portrait = fitted_portrait(344)
    center = (260, 226)
    radius = 172
    small_font = font(9)
    label_font = font(12, bold=True)

    for index in range(36):
        phase = index / 36
        canvas = Image.new("RGB", (width, height), BG)
        draw = ImageDraw.Draw(canvas, "RGBA")
        grid(draw, width, height, 24)
        draw.rounded_rectangle((2, 2, 517, 517), radius=22, outline=(0, 255, 136, 130), width=3)
        draw.text((20, 22), "BIOMETRIC_ID // SACHIN_T", font=small_font, fill=MUTED)
        pulse = int(120 + 135 * (0.5 + 0.5 * math.sin(phase * math.tau * 2)))
        draw.text((432, 22), "ONLINE", font=small_font, fill=GREEN)
        draw.ellipse((491, 20, 501, 30), fill=(0, 255, 136, pulse))

        paste_circle(canvas, portrait, center, radius)
        scanner(canvas, center, radius, (phase * 1.35) % 1)
        glow = glow_layer((width, height), lambda g: g.ellipse((83, 49, 437, 403), outline=(0, 255, 136, 170), width=4))
        canvas.paste(glow, (0, 0), glow)
        draw = ImageDraw.Draw(canvas, "RGBA")
        draw.ellipse((84, 50, 436, 402), outline=GREEN, width=3)
        animated_ring(draw, (70, 36, 450, 416), phase * 360, TEAL, 2)
        animated_ring(draw, (57, 23, 463, 429), -phase * 500, CYAN, 1)
        corners(draw, center, 150, pulse)
        draw.text((22, 134), "WEB", font=small_font, fill=TEAL)
        draw.text((17, 350), "OSINT", font=small_font, fill=TEAL)
        draw.text((466, 134), "VAPT", font=small_font, fill=TEAL)
        draw.text((475, 350), "NET", font=small_font, fill=TEAL)
        draw.rounded_rectangle((50, 455, 470, 501), radius=8, fill=(0, 255, 136, 10), outline=(0, 255, 136, 76), width=1)
        draw.text((260, 469), "IDENTITY MATCH // ACCESS AUTHORIZED", anchor="mm", font=small_font, fill=MUTED)
        draw.text((260, 489), "SACHIN T // VERIFIED", anchor="mm", font=label_font, fill=GREEN)
        frames.append(canvas)

    save_webp(frames, ASSETS / "sachin-cyber-avatar.webp", 100)


if __name__ == "__main__":
    render_header()
    render_avatar()
    print("Rendered animated profile assets.")
