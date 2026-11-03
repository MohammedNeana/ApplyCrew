#!/usr/bin/env python3
"""Stops private details reaching the dashboard. Prints CLEAN, or the private terms found in the export files."""
import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
terms_file = ROOT / "config" / "private_terms.txt"
terms = [t.strip() for t in terms_file.read_text(encoding="utf-8").splitlines() if t.strip() and not t.startswith("#")] if terms_file.exists() else []
files = [ROOT / "dashboard" / f for f in ("applications.json", "paused.json", "replies.json")]
text = "\n".join(f.read_text(encoding="utf-8") for f in files if f.exists()).lower()
digits = "".join(c for c in text if c.isdigit())
hits = []
for t in terms:
    d = "".join(c for c in t if c.isdigit())
    if t.lower() in text or (len(d) >= 7 and d == "".join(c for c in t if c.isdigit() or c in "+ -()").replace("+", "").replace(" ", "").replace("-", "").replace("(", "").replace(")", "") and d in digits):
        hits.append(t)
print(f"{len(hits)} private term(s) found, do not upload. Search the export files for each line of config/private_terms.txt." if hits else "CLEAN")
sys.exit(1 if hits else 0)
