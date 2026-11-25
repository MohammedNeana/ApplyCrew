#!/usr/bin/env python3
"""Writes the dataset document for each uploaded dashboard file, ready for one ArtifactData batch.

  python3 -I scripts/dataset_doc.py applications.json=/_blob/<id> briefing.json=/_blob/<id> ...

For each pair it writes tracker/.dataset_docs/<name>.json and prints one line:
  "<name> NEW <path>"       -> batch entry {op:"set", collection:"datasets", doc_id:<name>, file_path:<path>}  (no if_version)
  "<name> EXISTING <path>"  -> batch entry {op:"update", collection:"datasets", doc_id:<name>, file_path:<path>, if_version:<current>}
NEW means the file was never marked as uploaded (dash_changed.py --mark), for example briefing.json the first time
Sterling's note is switched on. A NEW dataset also gets a title and description.
"""
import datetime as dt, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tracker" / ".dataset_docs"
STATE = ROOT / "tracker" / ".dashboard_uploaded.json"
TITLES = {
    "applications": ("Applications", "Every application sent, with the posting, the questions and the answers. Contact details, salary and employment answers are kept private."),
    "paused": ("Waiting list", "Jobs paused because only the owner can finish them, and why."),
    "replies": ("Employer replies", "Each employer reply, in the employer's own words, without contact details or links."),
    "briefing": ("Sterling's note", "A short, pre-written note on the day: counts, fresh replies and what waits on the owner. Rebuilt on each refresh."),
}
now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
known = set(json.loads(STATE.read_text())) if STATE.exists() else set()
OUT.mkdir(parents=True, exist_ok=True)
for arg in sys.argv[1:]:
    name, _, url = arg.partition("=")
    name = pathlib.Path(name).name
    if not url.startswith("/_blob/") or not name.endswith(".json"):
        sys.exit(f"bad argument {arg!r}: expected <file>.json=/_blob/<id>")
    ds = name[:-5]
    doc = {"source": {"kind": "file", "url": url, "name": name, "format": "json"},
           "updated": {"at": now, "by": "Claude (job agent)"}}
    new = name not in known
    if new:
        title, desc = TITLES.get(ds, (ds.replace("_", " ").capitalize(), ""))
        doc.update({"title": title, "description": desc, "schedule": "Re-uploaded by Claude after each refresh"})
    p = OUT / f"{ds}.json"
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    print(ds, "NEW" if new else "EXISTING", p)
