#!/usr/bin/env python3
"""Keeps the optional companion pages current: Sterling (briefing) and Ashford (interview prep).

"python3 -I scripts/live_pages.py" rebuilds sterling/sterling_data.json from the public dashboard files, runs
selfcheck.py, and prints which page needs republishing: "STERLING CHANGED", "ASHFORD CHANGED: <files>", or
"NO CHANGE". "--mark" records the current state after a successful publish. "--build-only" only rebuilds the data.
Pages switched off in config/pages.json are skipped.
"""
import hashlib, json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DASH, STER, ASH = ROOT / "dashboard", ROOT / "sterling", ROOT / "ashford"
STATE = ROOT / "tracker" / ".live_pages_state.json"
try: CONF = json.loads((ROOT / "config" / "pages.json").read_text(encoding="utf-8"))
except Exception: CONF = {}


def load(name):
    try: return json.loads((DASH / name).read_text(encoding="utf-8"))
    except Exception: return []


def build_sterling_data():
    apps, reps, pau = load("applications.json"), load("replies.json"), load("paused.json")
    out = {
        "meta": {k: CONF.get(k, "") for k in ("first_name", "time_zone", "focus_label", "focus_countries", "dashboard_url", "ashford_url", "supporters_note")},
        "apps_cols": ["date", "company", "role", "country", "channel", "track", "status", "mark", "at"],
        "apps": [[a.get("date"), a.get("company"), a.get("role"), a.get("country"), a.get("channel"), a.get("track"), a.get("status"), a.get("mark") or "", a.get("at") or ""] for a in apps],
        "replies_cols": ["date", "company", "role", "outcome", "reason", "at"],
        "replies": [[r.get("date"), r.get("company"), r.get("role"), r.get("outcome"), (r.get("reason") or "")[:160], r.get("at") or ""] for r in reps],
        "needs_cols": ["date", "job", "state", "reason"],
        "needs": [[p.get("date"), (p.get("job") or "")[:120], p.get("state"), (p.get("reason") or "")[:160]] for p in pau],
    }
    # Compact: low-variety columns are stored as an index into out["dicts"]["<table>.<column>"] (the page decodes them).
    out["dicts"] = {}
    for table, cols in (("apps", ("country", "channel", "track", "status", "mark")), ("replies", ("outcome",)), ("needs", ("state",))):
        for c in cols:
            i = out[table + "_cols"].index(c)
            vals = sorted({str(r[i] or "") for r in out[table]})
            pos = {v: n for n, v in enumerate(vals)}
            out["dicts"][f"{table}.{c}"] = vals
            for r in out[table]: r[i] = pos[str(r[i] or "")]
    text = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    STER.mkdir(parents=True, exist_ok=True)
    if not (STER / "sterling_data.json").exists() or (STER / "sterling_data.json").read_text(encoding="utf-8") != text:
        (STER / "sterling_data.json").write_text(text, encoding="utf-8")


def digest(paths):
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.exists()}


if CONF.get("sterling"): build_sterling_data()
if sys.argv[1:] == ["--build-only"]:  # dash_changed.py calls this so its self-check compares fresh data
    sys.exit(0)
if sys.argv[1:] != ["--mark"]:  # never report a page as ready to publish when a public file fails the self-check
    chk = subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / "selfcheck.py")], capture_output=True, text=True)
    if chk.returncode != 0:
        print(chk.stdout.strip() or "SELFCHECK FAILED: " + chk.stderr.strip()[-300:]); sys.exit(1)
now = {
    "sterling": digest([STER / "sterling.html", STER / "sterling_data.json"]) if CONF.get("sterling") else {},
    "ashford": digest([ASH / "ashford.html", *sorted((ASH / "preps").glob("*.json"))]) if CONF.get("ashford") else {},
}
if sys.argv[1:] == ["--mark"]:
    STATE.write_text(json.dumps(now, indent=1))
    sys.exit(0)
old = json.loads(STATE.read_text()) if STATE.exists() else {}
said = False
if now["sterling"] and now["sterling"] != old.get("sterling"):
    print("STERLING CHANGED"); said = True
changed = [k for k, v in now["ashford"].items() if old.get("ashford", {}).get(k) != v]
removed = set(old.get("ashford", {})) - set(now["ashford"]) if CONF.get("ashford") else set()
if changed or removed:
    print("ASHFORD CHANGED: " + " ".join(changed + [f"{k} (removed)" for k in sorted(removed)])); said = True
if not said:
    print("NO CHANGE")
