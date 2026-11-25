#!/usr/bin/env python3
"""Ashford sync: tracker/ashford/<slug>.json -> index.json, the page's data (ashford/preps/) and applications/<folder>/prep.md.

Standard library only. Run: python3 -I scripts/ashford_sync.py
Then republish the Ashford page as ASHFORD_BRIEF.md describes. Exits non-zero, and copies nothing, if any prep
contains a line of config/private_terms.txt, an email address, a phone number or a money figure.
"""
import datetime as dt, json, pathlib, re, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "tracker" / "ashford"
PAGE = ROOT / "ashford" / "preps"
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE = re.compile(r"\+\d[\d\s\-()]{7,}\d")
MONEY = re.compile(r"(?i)\b(sar|aed|qar|usd|eur|gbp|cad|aud|inr|sgd|kwd|bhd|omr|egp|tnd)\s?\d[\d,.]*|[$€£]\s?\d[\d,.]*|\d[\d,.]*\s?k?\s?(dirhams?|riyals?|dinars?|pounds?|dollars?|euros?|rupees?)\b")


def private_terms():
    f = ROOT / "config" / "private_terms.txt"
    return [t.strip() for t in f.read_text(encoding="utf-8").splitlines() if t.strip() and not t.startswith("#")] if f.exists() else []


def term_rx(t):
    """The term, case-insensitive. A figure or phone number also matches with other separators or none."""
    if sum(c.isdigit() for c in t) >= 4 and re.fullmatch(r"[\d\s,.+\-()]+", t):
        return re.compile(r"(?<!\d)" + r"[\s,.\-()]*".join(re.sub(r"\D", "", t)) + r"(?!\d)")
    return re.compile(re.escape(t), re.I)


def page_meta():
    """Names and links the page shows, from config/pages.json. Nothing else from config reaches the page."""
    try: c = json.loads((ROOT / "config" / "pages.json").read_text(encoding="utf-8"))
    except Exception: c = {}
    return {k: c.get(k, "") for k in ("first_name", "time_zone", "dashboard_url", "sterling_url")}


def md(d):
    L = [f"# Ashford prep: {d['company']} - {d['role']}", "",
         f"- Stage: {d.get('stage','')} · Status: {d.get('status','')} · Updated: {d.get('updated','')}",
         f"- When: {d.get('deadline_text') or d.get('deadline') or 'no date yet'}"]
    if d.get("invitation"): L.append(f"- Invitation: {d['invitation']}")
    def bullets(title, items):
        if items: L.extend(["", f"## {title}", ""] + [f"- {x}" for x in items])
    bullets("Cheat sheet (read 10 minutes before)", d.get("cheat_sheet"))
    bullets("The company", d.get("brief"))
    if d.get("fit"):
        L += ["", "## You vs. the role", "", "| They want | You have |", "|---|---|"]
        L += [f"| {f['req']} | {f['me']} |".replace("\n", " ") for f in d["fit"]]
    if d.get("likely_questions"):
        L += ["", "## Likely questions and draft answers"]
        for q in d["likely_questions"]:
            L += ["", f"### {q['q']}", f"*Why they ask:* {q.get('why','')}", "", q.get("answer", "")]
    if d.get("technical_topics"):
        L += ["", "## Topics to refresh", ""] + [f"- **{t['topic']}**: {t['refresher']}" for t in d["technical_topics"]]
    bullets("Take-home plan", d.get("take_home_plan"))
    bullets("Questions to ask them", d.get("questions_to_ask"))
    bullets("Checklist", d.get("logistics"))
    if d.get("sources"):
        L += ["", "## Sources", ""] + [f"- [{s.get('title') or s['url']}]({s['url']})" for s in d["sources"]]
    return "\n".join(L) + "\n"


def main():
    SRC.mkdir(parents=True, exist_ok=True)
    terms = [(t, term_rx(t)) for t in private_terms()]
    preps, problems = [], []
    for f in sorted(SRC.glob("*.json")):
        if f.name == "index.json": continue
        text = f.read_text(encoding="utf-8")
        try: d = json.loads(text)
        except Exception as e: problems.append(f"{f.name}: invalid JSON ({e})"); continue
        for t, rx in terms:
            if rx.search(text): problems.append(f"{f.name}: contains a line of config/private_terms.txt")
        for rx, what in ((EMAIL, "an email address"), (PHONE, "a phone number"), (MONEY, "a money figure")):
            m = rx.search(text)
            if m: problems.append(f"{f.name}: {what}")
        if not re.fullmatch(r"[a-z0-9-]+", str(d.get("slug", ""))) or d.get("slug") != f.stem:
            problems.append(f"{f.name}: slug must be lowercase letters, digits and hyphens, and match the file name")
        preps.append((f, d))
    if problems:
        print("PRIVACY STOP:\n  " + "\n  ".join(problems)); sys.exit(1)
    rank = {"upcoming": 0, "submitted": 1, "done": 2}
    preps.sort(key=lambda x: (rank.get(x[1].get("status"), 3), x[1].get("deadline") or "9999"))
    index = {"updated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"), "meta": page_meta(),
             "preps": [{"slug": d["slug"], "company": d["company"], "role": d["role"], "stage": d.get("stage", ""),
                        "status": d.get("status", "upcoming"), "deadline": d.get("deadline", "")} for _, d in preps]}
    try:  # idempotent: keep the old timestamp when nothing changed, so the page isn't republished for nothing
        prev = json.loads((SRC / "index.json").read_text(encoding="utf-8"))
        unchanged = prev.get("preps") == index["preps"] and prev.get("meta") == index["meta"] and \
            all((PAGE / f.name).exists() and (PAGE / f.name).read_bytes() == f.read_bytes() for f, _ in preps)
        if unchanged and prev.get("updated"): index["updated"] = prev["updated"]
    except Exception:
        pass
    text = json.dumps(index, ensure_ascii=False, indent=1)
    if not (SRC / "index.json").exists() or (SRC / "index.json").read_text(encoding="utf-8") != text:
        (SRC / "index.json").write_text(text, encoding="utf-8")
    PAGE.mkdir(parents=True, exist_ok=True)
    keep = {"index.json"} | {f.name for f, _ in preps}
    for old in PAGE.glob("*.json"):
        if old.name not in keep: old.unlink()  # a prep removed from tracker/ashford leaves the page too
    shutil.copy2(SRC / "index.json", PAGE / "index.json")
    for f, d in preps:
        shutil.copy2(f, PAGE / f.name)
        folder = (d.get("applied") or {}).get("folder")
        if folder and (ROOT / folder).is_dir():
            (ROOT / folder / "prep.md").write_text(md(d), encoding="utf-8")
    print(f"ashford: {len(preps)} preps -> {PAGE.relative_to(ROOT)}; upcoming: {sum(1 for _, d in preps if d.get('status') == 'upcoming')}")


if __name__ == "__main__":
    main()
