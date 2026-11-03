#!/usr/bin/env python3
"""Build APPLICATIONS.md (one row per submitted application, newest first) from tracker/applied_log.jsonl."""
import json, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parent.parent
rows = []
for line in (ROOT/"tracker"/"applied_log.jsonl").read_text(encoding="utf-8").splitlines():
    line = line.strip()
    if not line: continue
    try: rows.append(json.loads(line))
    except Exception: pass
seen, uniq = set(), []
for r in rows:
    k = (r.get("company","").lower(), r.get("title","").lower())
    if k in seen: continue
    seen.add(k); uniq.append(r)
uniq.sort(key=lambda r: r.get("date",""), reverse=True)
by_country = collections.Counter((r.get("location","") or "?").split(",")[-1].strip() for r in uniq)
out = [f"# Applications sent ({len(uniq)} total)\n",
       "Each row links to the job and to the report with every question and answer.\n",
       "| # | Date | Company | Role | Location | Channel | Salary given | Job | Report |", "|---|---|---|---|---|---|---|---|---|"]
for i, r in enumerate(uniq, 1):
    out.append(f"| {i} | {r.get('date','')} | {r.get('company','')} | {r.get('title','')} | {r.get('location','')} | {r.get('channel','')} | {r.get('salary_given','') or '-'} | [link]({r.get('url','')}) | [report]({r.get('report','')}) |")
out.append("\n## By location\n" + "\n".join(f"- {k}: {v}" for k, v in by_country.most_common()))
(ROOT/"APPLICATIONS.md").write_text("\n".join(out)+"\n", encoding="utf-8")
print(f"{len(uniq)} applications indexed")
