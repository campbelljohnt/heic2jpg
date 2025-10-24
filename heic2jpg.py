#!/usr/bin/env python3
"""
HEIC → JPG (GPS preserved) — Minimal picker (with credit message)

Exactly what you asked for: the ONLY UI is two native folder pickers.
You choose the input folder (with .HEIC/.HEIF) and the output folder for .JPGs,
then it runs automatically. No window, no extra controls.

Defaults:
  • Recurses subfolders and mirrors the input tree in the output.
  • Preserves EXIF (including GPS) and fixes orientation (if piexif available).
  • Skips existing JPGs (no overwrite) unless you pass --overwrite.
  • JPEG quality 95.

Deps:
    pip install pillow pillow-heif piexif

Usage:
    python heic_to_jpg_min.py            # pops two pickers, runs
    python heic_to_jpg_min.py --overwrite --quality 92

Self-test (no HEICs needed):
    python heic_to_jpg_min.py --selftest
"""

import argparse
import sys
from pathlib import Path
from typing import Iterable, Optional

# Tk only for the two folder dialogs
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageOps

# Lazy HEIC support so missing native deps don't crash startup
try:
    import pillow_heif  # type: ignore
    _HEIF_AVAILABLE = True
except Exception:
    pillow_heif = None  # type: ignore
    _HEIF_AVAILABLE = False

try:
    import piexif  # type: ignore
except Exception:
    piexif = None

HEIC_EXTS = {".heic", ".heif", ".HEIC", ".HEIF"}

# Customize your end-of-run credit message here
AUTHOR_CREDIT = "Make sure you thank John Campbell for making this converter tool!"


def find_heic_files(root: Path) -> Iterable[Path]:
    return [p for p in root.rglob("*") if p.is_file() and p.suffix in HEIC_EXTS]


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def make_output_path(src: Path, input_root: Path, output_root: Path) -> Path:
    rel = src.relative_to(input_root)
    return (output_root / rel).with_suffix(".jpg")


def _fix_orientation_exif_bytes(exif_bytes: Optional[bytes]) -> Optional[bytes]:
    if not exif_bytes or not piexif:
        return exif_bytes
    try:
        exif_dict = piexif.load(exif_bytes)
        if piexif.ImageIFD.Orientation in exif_dict.get("0th", {}):
            exif_dict["0th"][piexif.ImageIFD.Orientation] = 1
        return piexif.dump(exif_dict)
    except Exception:
        return exif_bytes


def convert_one(src: Path, dest: Path, quality: int, overwrite: bool, fix_orientation: bool) -> str:
    try:
        if dest.exists() and not overwrite:
            return f"SKIP (exists): {src.name}"
        ensure_parent(dest)
        with Image.open(src) as img:
            exif_bytes = img.info.get("exif")
            if fix_orientation:
                img = ImageOps.exif_transpose(img)
                exif_bytes = _fix_orientation_exif_bytes(exif_bytes)
            img = img.convert("RGB")
            img.save(dest, format="JPEG", exif=exif_bytes, quality=quality, subsampling=0, optimize=True)
        return f"OK: {src.name}"
    except Exception as e:
        return f"ERROR: {src.name} ({e})"


def run_batch(input_dir: Path, output_dir: Path, quality: int, overwrite: bool, fix_orientation: bool) -> tuple[int, int, int]:
    if not _HEIF_AVAILABLE:
        raise RuntimeError(
            "HEIC support not available. Install pillow-heif (and libheif on Linux)."
        )
    try:
        pillow_heif.register_heif_opener()  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(f"HEIF initialization failed: {e}")

    files = list(find_heic_files(input_dir))
    total = len(files)
    done = 0
    errors = 0
    for src in files:
        dest = make_output_path(src, input_dir, output_dir)
        msg = convert_one(src, dest, quality, overwrite, fix_orientation)
        print(msg)
        done += 1
        if msg.startswith("ERROR"):
            errors += 1
    return total, done, errors


def pick_folders() -> tuple[Optional[Path], Optional[Path]]:
    root = tk.Tk()
    root.withdraw()
    root.update_idletasks()
    in_dir = filedialog.askdirectory(title="Select input folder with HEIC files")
    if not in_dir:
        return None, None
    out_dir = filedialog.askdirectory(title="Select output folder for JPG files")
    if not out_dir:
        return None, None
    return Path(in_dir), Path(out_dir)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Convert HEIC/HEIF to JPG (GPS preserved) with minimal UI for folder picking.")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing JPGs")
    p.add_argument("--quality", type=int, default=95, help="JPEG quality (1-100)")
    p.add_argument("--no-orient-fix", action="store_true", help="Do not apply EXIF orientation fix")
    p.add_argument("--selftest", action="store_true", help="Run built-in tests and exit")
    return p.parse_args()


# ----------------------
# Minimal self-tests
# ----------------------

def _selftest() -> int:
    import tempfile
    # ensure path mapping works
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        src_root = root / "in/sub"
        dst_root = root / "out"
        src_root.mkdir(parents=True)
        fake = src_root / "x.HEIC"
        fake.write_bytes(b"not-heic")
        dest = make_output_path(fake, root / "in", dst_root)
        ensure_parent(dest)
        assert dest.parent.exists()
    # orientation no-op
    assert _fix_orientation_exif_bytes(None) is None
    print("Self-test passed.")
    return 0


if __name__ == "__main__":
    args = parse_args()
    if args.selftest:
        sys.exit(_selftest())

    # 1) Pick folders (the only UI)
    src, dst = pick_folders()
    if not src or not dst:
        print("Cancelled.")
        sys.exit(0)

    # 2) Validate and run
    try:
        if not src.exists() or not src.is_dir():
            raise FileNotFoundError(f"Input directory not found: {src}")
        dst.mkdir(parents=True, exist_ok=True)
        total, done, errs = run_batch(
            input_dir=src,
            output_dir=dst,
            quality=max(1, min(100, int(args.quality))),
            overwrite=bool(args.overwrite),
            fix_orientation=not args.no_orient_fix,
        )
        # Final messages (newline-escaped to avoid SyntaxError)
        tk.Tk().withdraw()
        messagebox.showinfo("HEIC → JPG", f"Processed {done}/{total}. Errors: {errs}\n\n{AUTHOR_CREDIT}")
        print(f"Processed {done}/{total}. Errors: {errs}\n{AUTHOR_CREDIT}")
    except Exception as e:
        tk.Tk().withdraw()
        messagebox.showerror("HEIC → JPG - Error", str(e))
        raise
