#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate icon.png and fanart.png with stdlib only (Douyin-like cyan/magenta)."""
from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "plugin.video.douyin" / "resources" / "media"

CYAN = (37, 244, 238, 255)
MAGENTA = (254, 44, 85, 255)
BG = (12, 12, 16, 255)


def _png(width, height, rgba_rows):
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + bytes(row) for row in rgba_rows)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def _blend(dst, src):
    sa = src[3] / 255.0
    if sa <= 0:
        return dst
    out = []
    for i in range(3):
        out.append(int(src[i] * sa + dst[i] * (1 - sa)))
    out.append(255)
    return tuple(out)


def _circle(pixels, w, h, cx, cy, r, color, feather=2.5):
    for y in range(max(0, int(cy - r - 3)), min(h, int(cy + r + 4))):
        row = pixels[y]
        for x in range(max(0, int(cx - r - 3)), min(w, int(cx + r + 4))):
            d2 = (x - cx) ** 2 + (y - cy) ** 2
            if d2 > (r + feather) ** 2:
                continue
            d = math.sqrt(d2)
            if d <= r - feather:
                a = 1.0
            else:
                a = max(0.0, 1.0 - (d - (r - feather)) / (feather * 2))
            src = (color[0], color[1], color[2], int(color[3] * a))
            i = x * 4
            cur = (row[i], row[i + 1], row[i + 2], row[i + 3])
            nxt = _blend(cur, src)
            row[i : i + 4] = nxt


def _note(pixels, w, h, cx, cy, scale, color):
    _circle(pixels, w, h, cx, cy + 10 * scale, 28 * scale, color, feather=3)
    _circle(pixels, w, h, cx + 38 * scale, cy - 6 * scale, 22 * scale, color, feather=3)
    x0, x1 = int(cx + 20 * scale), int(cx + 28 * scale)
    y0, y1 = int(cy - 70 * scale), int(cy + 8 * scale)
    for y in range(max(0, y0), min(h, y1)):
        row = pixels[y]
        for x in range(max(0, x0), min(w, x1)):
            i = x * 4
            nxt = _blend((row[i], row[i + 1], row[i + 2], row[i + 3]), color)
            row[i : i + 4] = nxt


def icon(path: Path, size=512):
    pixels = [bytearray(BG * size) for _ in range(size)]
    _note(pixels, size, size, size * 0.32, size * 0.50, 2.15, CYAN)
    _note(pixels, size, size, size * 0.46, size * 0.56, 2.15, MAGENTA)
    path.write_bytes(_png(size, size, pixels))
    print("wrote", path, path.stat().st_size)


def fanart(path: Path, w=1280, h=720):
    pixels = [bytearray(BG * w) for _ in range(h)]
    _circle(pixels, w, h, w * 0.28, h * 0.52, 260, CYAN, feather=90)
    _circle(pixels, w, h, w * 0.70, h * 0.48, 300, MAGENTA, feather=110)
    _circle(pixels, w, h, w * 0.52, h * 0.50, 140, (20, 20, 28, 220), feather=40)
    path.write_bytes(_png(w, h, pixels))
    print("wrote", path, path.stat().st_size)


def main():
    MEDIA.mkdir(parents=True, exist_ok=True)
    icon_path = MEDIA / "icon.png"
    fan_path = MEDIA / "fanart.png"
    if not icon_path.exists() or icon_path.stat().st_size < 1000:
        icon(icon_path)
    if not fan_path.exists() or fan_path.stat().st_size < 1000:
        fanart(fan_path)


if __name__ == "__main__":
    main()
