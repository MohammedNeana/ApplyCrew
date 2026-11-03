#!/usr/bin/env python3
"""Creates your private folders from the blank templates. Never overwrites a file that already exists."""
import pathlib, shutil
ROOT = pathlib.Path(__file__).resolve().parent.parent
for d in ("cv", "applications", "profile/cv_text"):
    (ROOT / d).mkdir(parents=True, exist_ok=True)
made = 0
for src in (ROOT / "blank").rglob("*"):
    if src.is_dir(): continue
    dst = ROOT / src.relative_to(ROOT / "blank")
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.exists():
        shutil.copy2(src, dst); made += 1
print(f"Workspace ready, {made} new files.")
