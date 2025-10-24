# README.md

## HEIC → JPG Converter (GPS Preserved)

### Overview
This project provides a **simple and fast tool** for converting **HEIC/HEIF** photos (the default image format on iPhones) to **JPG** while retaining **EXIF metadata**—especially **GPS coordinates**. It was built to help field data collectors who use iOS devices capture project photos with location data and need an easy way to convert them for use in reports, GIS tools, or project archives.

Many free or built‑in converters strip GPS and other EXIF data during conversion. Paid tools exist, but this project aims to do the job **transparently, offline, and free**.

### The Story
Field data collectors often export images directly from their iPhones as **.HEIC** files. These files contain valuable GPS metadata, but Windows‑based systems and many conversion tools remove that data when saving to JPG. To solve this, **John Campbell** created a lightweight Python utility that preserves GPS coordinates and other EXIF tags during conversion.

### Features
- 🔍 Preserves all EXIF data (GPS, timestamps, orientation, etc.)
- 🧭 Retains accurate GPS coordinates for mapping workflows
- ⚙️ Automatically fixes orientation based on EXIF tags
- 🗂️ Recursively converts all HEIC files in a folder
- 🪶 Simple two‑click interface (just pick input/output folders)
- 💡 Works as a standalone EXE (no Python required for users)
- 🧾 Includes built‑in self‑test for verification

### Dependencies (for Python version)
```bash
pip install pillow pillow-heif piexif
```

### Usage (Python Script)
```bash
python heic_to_jpg_min.py
```
The program will prompt you to:
1. Select the input folder containing HEIC images.
2. Select the output folder for converted JPG files.

It then automatically processes all HEIC/HEIF files, preserving metadata and showing a completion message.

Optional flags:
```bash
python heic_to_jpg_min.py --overwrite --quality 90
```

### Creating the EXE
To distribute as a standalone Windows app:
```bash
pip install pyinstaller
pyinstaller --onefile --windowed heic_to_jpg_min.py --collect-all pillow_heif --collect-all PIL
```
The resulting EXE will appear in the `dist/` folder. It can run on any Windows machine **without Python installed**.

### Example Output Message
```
Processed 217/217. Errors: 0
