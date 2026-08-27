#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build an installable Kodi zip: plugin.video.douyin/addon.xml at archive root+1."""
from __future__ import annotations

import base64
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "plugin.video.douyin"
DIST = ROOT / "dist"
MEDIA = ADDON / "resources" / "media"
SKIP = {".b64", ".pyc"}
sys.path.insert(0, str(Path(__file__).resolve().parent))


def decode_art():
    MEDIA.mkdir(parents=True, exist_ok=True)
    for name in ("icon.png", "fanart.png"):
        target = MEDIA / name
        b64 = MEDIA / (name + ".b64")
        if target.exists() and target.stat().st_size > 1000:
            continue
        if b64.exists():
            target.write_bytes(base64.b64decode(b64.read_text(encoding="ascii")))
            print("decoded", target.name, target.stat().st_size)
            continue
        from make_art import main as draw

        draw()
        if not target.exists():
            raise SystemExit("missing artwork %s" % target)


def version():
    xml = (ADDON / "addon.xml").read_text(encoding="utf-8")
    m = re.search(r'<addon\b[^>]*\bversion="([^"]+)"', xml)
    if not m:
        raise SystemExit("cannot read version from addon.xml")
    return m.group(1)


def pack():
    decode_art()
    ver = version()
    DIST.mkdir(parents=True, exist_ok=True)
    zip_path = DIST / ("plugin.video.douyin-%s.zip" % ver)
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(ADDON.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix in SKIP or path.name.endswith(".b64"):
                continue
            if path.name in (".DS_Store", ".gitkeep") or "__pycache__" in path.parts:
                continue
            arc = Path("plugin.video.douyin") / path.relative_to(ADDON)
            zf.write(path, arc.as_posix())
            print(" +", arc.as_posix())
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
    if "plugin.video.douyin/addon.xml" not in names:
        raise SystemExit("zip structure invalid: addon.xml not in plugin.video.douyin/")
    if "plugin.video.douyin/resources/media/icon.png" not in names:
        raise SystemExit("zip missing icon.png")
    if "plugin.video.douyin/resources/media/fanart.png" not in names:
        raise SystemExit("zip missing fanart.png")
    print("wrote", zip_path, "(%s bytes, %s files)" % (zip_path.stat().st_size, len(names)))
    return zip_path


if __name__ == "__main__":
    pack()
