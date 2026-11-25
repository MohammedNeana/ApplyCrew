#!/usr/bin/env python3
"""Fills the dashboard page with the owner's name, focus region and any companion page links from config/pages.json, writing dashboard/index_doc.json for files/index.html.
Usage: make_dashboard_page.py "<First name>" "<Focus label>" '<JSON list of country names as in dashboard/world.json>'"""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
owner, label, focus = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
html = (ROOT / "dashboard" / "page_template.html").read_text(encoding="utf-8")
names = {c["name"] for c in json.loads((ROOT / "dashboard" / "world.json").read_text(encoding="utf-8"))}
unknown = [c for c in focus if c not in names]
if unknown: print("Not in world.json, so check the spelling:", unknown)
try: pages = json.loads((ROOT / "config" / "pages.json").read_text(encoding="utf-8"))
except Exception: pages = {}
links = [(n, sub, pages.get(k, "")) for n, sub, k in (("Sterling", "briefing", "sterling_url"), ("Ashford", "coach", "ashford_url")) if str(pages.get(k, "")).startswith("https://")]
nav = ('  <nav class="jh-suite" aria-label="Job hunt pages">\n    <span class="here" aria-current="page">Dashboard</span>\n'
       + "".join(f'    <a href="{u.replace(chr(34), "%22").replace("<", "%3C")}" target="_blank" rel="noopener">{n} <small>{sub}</small></a>\n' for n, sub, u in links) + "  </nav>") if links else ""
html = html.replace("{{SUITE_NAV}}", nav)
for k, v in (("{{OWNER}}", owner), ("{{FOCUS_LABEL}}", label), ("{{FOCUS_NOTE}}", ", ".join(focus)), ("{{FOCUS_JSON}}", json.dumps(focus, ensure_ascii=False))):
    html = html.replace(k, v)
(ROOT / "dashboard" / "index_doc.json").write_text(json.dumps({"text": html}, ensure_ascii=False), encoding="utf-8")
print("Wrote dashboard/index_doc.json")
