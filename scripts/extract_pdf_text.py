#!/usr/bin/env python3
"""Extract plain text from CV PDFs so the agent can read them.
usage: python3 -I scripts/extract_pdf_text.py cv profile/cv_text      (needs: pip install pypdf)
Check the output: if the text looks garbled (broken letters), ATS parsers will read your PDF badly; re-export the PDF."""
import sys, pathlib
from pypdf import PdfReader
src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "cv")
out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else "profile/cv_text"); out.mkdir(parents=True, exist_ok=True)
for pdf in sorted(list(src.glob("*.pdf")) + list((src/"_candidates").glob("*.pdf"))):
    pages = 0
    try:
        r = PdfReader(str(pdf)); pages = len(r.pages); txt = "\n".join((p.extract_text() or "") for p in r.pages)
    except Exception as e:
        txt = f"[extract failed: {e}]"
    (out / (pdf.stem + ".txt")).write_text(txt, encoding="utf-8")
    print(f"{pdf.name}: {pages} pages, {len(txt)} chars")
