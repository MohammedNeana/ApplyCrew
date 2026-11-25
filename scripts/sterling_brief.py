#!/usr/bin/env python3
"""Sterling's note for the top of the dashboard: dashboard/briefing.json.

Standard library only, no LLM, and the same output for the same day and data. Reads ONLY the public-safe
dashboard files (applications.json, replies.json, paused.json), plus company and stage from
tracker/ashford/index.json, and the first name in config/pages.json. The note may be public: company, role,
country and counts only. No emails, phone numbers, pay, people's names or chat content.
Run: python3 -I scripts/sterling_brief.py  (export_dashboard.py runs it at its end when Sterling is switched on)
"""
import datetime as dt, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DASH = ROOT / "dashboard"
OUT = DASH / "briefing.json"
ASHFORD_INDEX = ROOT / "tracker" / "ashford" / "index.json"  # Ashford's preps: only company and stage are read
MAX_ITEMS = 6
NEWS_DAYS = 2  # only fresh invitations are news; old ones the owner already handled are not

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE = re.compile(r"\+?\d[\d\s\-()]{7,}\d")
MONEY = re.compile(r"(?i)(sar|aed|qar|kwd|bhd|omr|egp|tnd|usd|eur|gbp|cad|aud|inr|\$|€|£)\s?[\d,.]+k?(\s?[-–]\s?(\$|€|£)?[\d,.]+k?)?(\s?/\s?\w+)?|[\d,.]+\s?k?\s?(sar|aed|qar|kwd|bhd|omr|egp|tnd|usd|eur|gbp|cad|aud|inr|dirhams?|riyals?|dinars?|pounds?|dollars?|euros?|rupees?)\b")
BANNED = re.compile(r"(?i)whats\s?app|telegram|salary|@|\bwa\.me\b")
WORDS = "zero one two three four five six seven eight nine ten eleven twelve".split()


def load(name):
    try:
        data = json.loads((DASH / name).read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def first_name():
    try: return str(json.loads((ROOT / "config" / "pages.json").read_text(encoding="utf-8")).get("first_name") or "").strip()
    except Exception: return ""


def clean(text, limit=70):
    t = str(text or "")
    t = re.sub(r"\([^)]*(\$|€|£|\d+\s?k\b|/hr|per hour|salary)[^)]*\)", "", t, flags=re.I)  # "($50-$100/hr ...)"
    t = MONEY.sub("", EMAIL.sub("", t))
    t = PHONE.sub("", t)
    t = re.sub(r"\s{2,}", " ", t).strip(" -–,;:|")
    if len(t) > limit:
        t = t[:limit].rsplit(" ", 1)[0].rstrip(" -–,;:(") + "…"
    return t


def num(n, cap=False):
    w = WORDS[n] if 0 <= n < len(WORDS) else f"{n:,}"
    return w[:1].upper() + w[1:] if cap else w


def names(items):
    items = list(items)
    if len(items) <= 1: return "".join(items)
    return ", ".join(items[:-1]) + " and " + items[-1]


def day_label(d):
    return f"{d.day} {d.strftime('%b')}"


def ckey(company):
    w = re.findall(r"[a-z0-9]+", (company or "").lower())
    return w[0] if w else ""


def main():
    now = dt.datetime.now().astimezone()
    today = now.date()
    yday = today - dt.timedelta(days=1)
    seed = today.toordinal()
    who = first_name()
    hello = f", {who}" if who else ""

    def pick(salt, options):  # varied wording, fixed for the day
        return options[(seed * 7 + salt) % len(options)]

    apps, replies, paused = load("applications.json"), load("replies.json"), load("paused.json")

    # ---- news: fresh interviews, assessments and recruiter replies, newest first, one per company
    rank = {"interview": 0, "assessment": 1, "recruiter_reply": 2, "offer": 0}
    since = (today - dt.timedelta(days=NEWS_DAYS - 1)).isoformat()
    cand = [(str(r["date"]), r["outcome"], r.get("company", ""), r.get("role", ""), r.get("map", ""))
            for r in replies if r.get("outcome") in rank and str(r.get("date", "")) >= since]
    rej = {}
    for r in replies:
        if r.get("outcome") == "rejected": rej[ckey(r.get("company", ""))] = max(rej.get(ckey(r.get("company", "")), ""), str(r.get("date", "")))
    cand = [c for c in cand if rej.get(ckey(c[2]), "") < c[0]]  # a later rejection cancels the news
    cand.sort(key=lambda c: (c[0], -rank[c[1]]), reverse=True)
    news, seen = [], set()
    for date, outcome, company, role, where in cand:
        k = ckey(company)
        if not k or k in seen: continue
        seen.add(k)
        comp = clean(company, 50)
        rl = clean(role, 60)
        if rl.lower() in ("", "technical role", "not stated in email", "unknown"): rl = ""
        place = "" if where in ("", "Remote") else f" ({where})"
        try: when = day_label(dt.date.fromisoformat(date[:10]))
        except ValueError: when = ""
        what = f" for {rl}" if rl else ""
        if outcome == "offer":
            text = f"An offer from {comp}{what}{place}, {when}. Do read it carefully before anything else."
            kind = "good"
        elif outcome == "interview":
            text = pick(1, [f"{comp} has an interview on the books{what}{place}, {when}.",
                            f"An interview with {comp}{what}{place}, {when}. Most encouraging.",
                            f"{comp}{place}: interview stage{what}, {when}. One does like to see it."])
            kind = "good"
        elif outcome == "assessment":
            text = pick(2, [f"{comp}{place} sent an assessment{what}, {when}. Progress.",
                            f"An assessment from {comp}{what}{place}, {when}. They are clearly paying attention.",
                            f"{comp} has moved to an assessment{what}{place}, {when}."])
            kind = "good"
        else:
            what = f" about {rl}" if rl else ""
            text = pick(3, [f"A recruiter at {comp} wrote back{what}{place}, {when}.",
                            f"{comp} replied in person{what}{place}, {when}. A real human, no less.",
                            f"A genuine reply from {comp}{what}{place}, {when}."])
            kind = "news"
        news.append({"kind": kind, "text": text})

    # ---- today's tally against yesterday (or yesterday's against the day before, early in the day)
    per_day = {}
    for a in apps:
        d = str(a.get("date", ""))[:10]
        per_day[d] = per_day.get(d, 0) + 1
    t_n, y_n = per_day.get(today.isoformat(), 0), per_day.get(yday.isoformat(), 0)
    b_n = per_day.get((today - dt.timedelta(days=2)).isoformat(), 0)
    rest = []
    if t_n == 0 and now.hour < 12:
        if y_n > b_n:
            text = pick(4, [f"Yesterday closed at {y_n} applications, comfortably ahead of the {b_n} the day before.",
                            f"{y_n} applications went out yesterday, beating the day before ({b_n}). Splendid.",
                            f"Yesterday's tally: {y_n}, up from {b_n}. The day has a fine act to follow."])
        else:
            text = pick(4, [f"Yesterday closed at {y_n} applications; the day before managed {b_n}. Today is young.",
                            f"{y_n} applications went out yesterday, against {b_n} the day before. A fresh page awaits.",
                            f"Yesterday's tally: {y_n} (the day before: {b_n}). We shall endeavour to improve on it."])
    elif t_n > y_n:
        text = pick(5, [f"{t_n} applications today, already past yesterday's {y_n}. Rather good going.",
                        f"Today stands at {t_n}, ahead of yesterday's {y_n}.",
                        f"{t_n} sent today against {y_n} yesterday: a new day, a better one."])
    else:
        text = pick(5, [f"{t_n} applications so far today, against {y_n} yesterday. Still {y_n - t_n + 1} to go to beat it.",
                        f"Today: {t_n} sent. Yesterday's {y_n} remains the mark to clear.",
                        f"{t_n} out the door today; {y_n - t_n + 1} more and yesterday is bettered."])
    rest.append({"kind": "count", "text": text})

    # ---- replies since yesterday: receipts counted, declines named lightly
    recent = [r for r in replies if str(r.get("date", ""))[:10] >= yday.isoformat()]
    rec = sum(1 for r in recent if r.get("outcome") == "received")
    if rec:
        rest.append({"kind": "count", "text": pick(6, [
            f"{num(rec, True)} applications acknowledged since yesterday. The usual automated courtesies." if rec > 1 else "One application acknowledged since yesterday. An automated courtesy, but a courtesy.",
            f"{num(rec, True)} 'we have received your application' notes since yesterday, duly filed." if rec > 1 else "One receipt since yesterday, duly filed.",
            f"{num(rec, True)} receipts have come in since yesterday. Filed." if rec > 1 else "A single receipt since yesterday. Filed."])})
    dec, dseen = [], set()
    for r in recent:
        if r.get("outcome") != "rejected": continue
        c = clean(r.get("company", ""), 40)
        if c and ckey(c) not in dseen:
            dseen.add(ckey(c)); dec.append(c)
    if dec:
        shown = dec[:3]
        tail = f" and {num(len(dec) - 3)} others" if len(dec) > 3 else ""
        listed = (", ".join(shown) + tail) if tail else names(shown)
        n = len(dec)
        if n == 1:
            text = pick(7, [f"One polite decline: {listed}. Their loss.", f"{listed} has declined, politely. Their loss.",
                            f"A single 'not at this time' from {listed}. Their loss."])
        else:
            text = pick(7, [f"{num(n, True)} polite declines: {listed}. Their loss.",
                            f"{num(n, True)} declines since yesterday: {listed}. Their loss entirely.",
                            f"{num(n, True)} firms have passed: {listed}. One wishes them well, and better judgement."])
        rest.append({"kind": "decline", "text": text})

    # ---- what waits on the owner
    wk = (today - dt.timedelta(days=6)).isoformat()  # only this week's items, so old ones don't pile up in the note
    wait = sum(1 for p in paused if p.get("state") == "Waiting" and str(p.get("date", "")) >= wk)
    tab = f"'Waiting on {who}'" if who else "the waiting list"
    if wait:
        rest.append({"kind": "waiting", "text": pick(8, [
            f"{wait} forms from this week are waiting on you, whenever you have a moment." if wait > 1 else "One form is waiting on you, whenever you have a moment.",
            f"{wait} items from this week await your attention under {tab}." if wait > 1 else f"One item awaits your attention under {tab}.",
            f"{wait} applications from this week are paused for a word from you." if wait > 1 else "One application is paused for a word from you."])})

    # ---- Ashford: one line when a prep for an upcoming interview or screening is ready (company and stage only)
    try:
        ash = json.loads(ASHFORD_INDEX.read_text(encoding="utf-8")).get("preps", [])
    except Exception:
        ash = []
    ready = []
    for pr in ash:
        if not isinstance(pr, dict) or pr.get("status") != "upcoming": continue
        comp = clean(pr.get("company", ""), 40)
        stage = clean(pr.get("stage", ""), 20).lower()
        if comp: ready.append(f"{comp} ({stage})" if stage else comp)
    if ready:
        rest.insert(0, {"kind": "news", "text": f"Ashford has your prep for {names(ready[:3])} ready."})

    items = news[:max(0, MAX_ITEMS - len(rest))] + rest
    items = [i for i in items if not BANNED.search(i["text"])][:MAX_ITEMS]

    h = now.hour
    if h < 5: greeting = pick(9, [f"Good evening{hello}.", f"Still up{hello}? Good evening.", f"Good evening{hello}. The small hours, I note."])
    elif h < 12: greeting = pick(9, [f"Good morning{hello}.", f"Good morning{hello}. Tea is poured.", f"A very good morning{hello}."])
    elif h < 17: greeting = pick(9, [f"Good afternoon{hello}.", f"Good afternoon{hello}. A word, if I may.", f"A very good afternoon{hello}."])
    else: greeting = pick(9, [f"Good evening{hello}.", f"Good evening{hello}. Your evening note.", f"A very good evening{hello}."])

    good = sum(1 for i in news if i["kind"] == "good")
    beat = (t_n > y_n) or (t_n == 0 and now.hour < 12 and y_n > b_n)
    if good:
        headline = pick(10, ["There is genuinely good news to open with.", "Let us begin with the good news, of which there is some.",
                             "Something worth a second cup: real progress this week."])
    elif news:
        headline = pick(10, ["A human or two has written back, which is always heartening.", "Correspondence of the non-automated kind has arrived.",
                             "The post brings a genuine reply or two."])
    elif beat:
        headline = pick(10, ["The tally is up on the day before, which is just as it should be.", "Steady work, and more of it than the day before.",
                             "The numbers are climbing nicely."])
    else:
        headline = pick(10, ["A steady day; the search carries on apace.", "Nothing dramatic to report, which is its own kind of progress.",
                             "All quiet on the correspondence front, and the work goes on."])
    for s in (greeting, headline):
        if BANNED.search(s): raise SystemExit("banned text in note")

    note = {"greeting": greeting, "headline": headline, "items": items}
    try:  # keep the old time when nothing changed, so the refresh sees no change to upload
        prev = json.loads(OUT.read_text(encoding="utf-8"))
        old = {"greeting": prev[0]["greeting"], "headline": prev[0]["headline"], "items": [{"kind": r["kind"], "text": r["text"]} for r in prev],
               "generated_at": prev[0].get("generated_at")}
        same = {k: old.get(k) for k in note} == note
    except Exception:
        old, same = {}, False
    generated = old.get("generated_at") if same and old.get("generated_at") else now.isoformat(timespec="minutes")
    # The dashboard's file loader reads a list of rows, so the note is written as one row per line.
    rows = [{"n": i + 1, "kind": it["kind"], "text": it["text"], "greeting": greeting, "headline": headline, "generated_at": generated}
            for i, it in enumerate(items)]
    text = json.dumps(rows, ensure_ascii=False, indent=1)
    if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
        OUT.write_text(text, encoding="utf-8")
    print(f"briefing: {len(items)} items, written {generated}")


if __name__ == "__main__":
    main()
