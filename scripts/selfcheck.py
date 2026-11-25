#!/usr/bin/env python3
"""Self-check of every file that may be published, before anything is uploaded or republished.

  python3 -I scripts/selfcheck.py            check; prints "SELFCHECK OK ..." or "SELFCHECK FAILED: ..." (exit 1)
  python3 -I scripts/selfcheck.py --accept   also accept the current counts as the new baseline (after a deliberate cleanup)
  python3 -I scripts/selfcheck.py --log      check tracker/applied_log.jsonl only: run it after appending a line

Checks: every line of config/private_terms.txt (a figure also matches without its separators, so 12,000 = 12000),
email addresses and phone numbers in the data files, JSON validity, count sanity (no sudden drops, no empty export),
duplicates, and size budgets. Standard library only. dash_changed.py and live_pages.py run it and refuse to report
changes when it fails, so a bad export never uploads.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DASH, STER, ASH = ROOT / "dashboard", ROOT / "sterling", ROOT / "ashford"
BASE = ROOT / "tracker" / ".selfcheck_counts.json"
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}")
PHONE = re.compile(r"\+\d[\d\s\-()]{7,}\d")
CHATS = re.compile(r"whats\s?app|telegram", re.I)  # private chats never go public; job texts may still name the products
NO_CHATS = {"replies.json", "paused.json", "briefing.json", "sterling_data.json"}
LIMITS = {"applications.json": 4_000_000, "replies.json": 3_000_000, "sterling_data.json": 1_500_000}


def private_terms():
    f = ROOT / "config" / "private_terms.txt"
    return [t.strip() for t in f.read_text(encoding="utf-8").splitlines() if t.strip() and not t.startswith("#")] if f.exists() else []


def term_rx(t):
    """The term, case-insensitive. A figure or phone number also matches with other separators or none."""
    if sum(c.isdigit() for c in t) >= 4 and re.fullmatch(r"[\d\s,.+\-()]+", t):
        return re.compile(r"(?<!\d)" + r"[\s,.\-()]*".join(re.sub(r"\D", "", t)) + r"(?!\d)")
    return re.compile(re.escape(t), re.I)


TERMS = [(t, term_rx(t)) for t in private_terms()]
problems = []


def scan(rel, text, json_file):
    for t, rx in TERMS:
        if rx.search(text): problems.append(f"{rel}: contains a line of config/private_terms.txt ({t[:3]}...)")
    if json_file:
        for rx, what in ((EMAIL, "an email address"), (PHONE, "a phone number")):
            m = rx.search(text)
            if m: problems.append(f"{rel}: {what} {m.group(0)[:4]}...")


def check_log():
    log = ROOT / "tracker" / "applied_log.jsonl"
    need = {"date", "company", "title", "url", "channel", "status"}
    for n, line in enumerate(log.read_text(encoding="utf-8").splitlines() if log.exists() else [], 1):
        if not line.strip(): continue
        try: r = json.loads(line)
        except Exception: problems.append(f"applied_log.jsonl line {n}: not valid JSON"); continue
        if not need <= set(r): problems.append(f"applied_log.jsonl line {n}: missing {sorted(need - set(r))}")
        if EMAIL.search(line): problems.append(f"applied_log.jsonl line {n}: an email address (keep addresses in report.md)")
    if problems:
        print("SELFCHECK FAILED: " + " | ".join(problems[:12])); sys.exit(1)
    print("SELFCHECK OK applied_log.jsonl")
    sys.exit(0)


if "--log" in sys.argv: check_log()


def public_files():
    files = [DASH / f for f in ("applications.json", "paused.json", "replies.json", "briefing.json")]
    files += [STER / "sterling.html", STER / "sterling_data.json", ASH / "ashford.html"]
    files += sorted((ASH / "preps").glob("*.json"))
    return [f for f in files if f.exists()]


data = {}
for f in public_files():
    rel, text = f.relative_to(ROOT), f.read_text(encoding="utf-8")
    scan(rel, text, f.suffix == ".json")
    if f.name in NO_CHATS and CHATS.search(text): problems.append(f"{rel}: mentions a private chat app")
    if f.suffix == ".json":
        try: data[f.name] = json.loads(text)
        except Exception as e: problems.append(f"{rel}: invalid JSON ({e})")
    cap = LIMITS.get(f.name)
    if cap and f.stat().st_size > cap: problems.append(f"{rel}: {f.stat().st_size:,} bytes, over the {cap:,} budget")

apps = data.get("applications.json")
reps = data.get("replies.json")
paused = data.get("paused.json")
if not isinstance(apps, list): problems.append("applications.json: missing or not a list"); apps = []
if not isinstance(reps, list): problems.append("replies.json: missing or not a list"); reps = []
if not isinstance(paused, list): problems.append("paused.json: missing or not a list"); paused = []

urls = [a.get("url") for a in apps]
if len(set(urls)) != len(urls): problems.append(f"applications.json: {len(urls) - len(set(urls))} duplicate urls")
need = {"date", "company", "role", "country", "channel", "status", "url"}
bad = [a.get("url") for a in apps if not need <= set(a)]
if bad: problems.append(f"applications.json: {len(bad)} rows miss list fields")
dangling = sum(1 for x in reps if isinstance(x, dict) and x.get("app_url") and x["app_url"] not in set(urls))
if dangling: problems.append(f"replies.json: {dangling} replies point at an application that is not listed")

sd = data.get("sterling_data.json")  # Sterling must describe the same applications as the dashboard
if isinstance(sd, dict) and len(sd.get("apps") or []) != len(apps):
    problems.append(f"sterling_data.json: {len(sd.get('apps') or [])} applications vs {len(apps)} on the dashboard")

counts = {"applications": len(apps), "replies": len(reps), "paused": len(paused)}
old = json.loads(BASE.read_text()) if BASE.exists() else {}
for k, v in counts.items():
    o = old.get(k, 0)
    if o >= 20 and v < o * 0.9: problems.append(f"{k}: dropped from {o} to {v} (over 10%); run with --accept if deliberate")

if problems:
    print("SELFCHECK FAILED: " + " | ".join(problems[:12]) + (f" | ... {len(problems) - 12} more" if len(problems) > 12 else ""))
    sys.exit(1)
new = counts if "--accept" in sys.argv else {k: max(v, old.get(k, 0)) for k, v in counts.items()}  # follows growth, never a drop
if new != old and BASE.parent.exists(): BASE.write_text(json.dumps(new))
print("SELFCHECK OK " + ", ".join(f"{k} {v}" for k, v in counts.items()) + f"; {len(public_files())} public files clean")
