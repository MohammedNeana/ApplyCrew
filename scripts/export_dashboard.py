#!/usr/bin/env python3
"""Export tracker data to dashboard/applications.json and dashboard/paused.json for the live dashboard."""
import json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
ALIASES = [(r"uae|dubai|abu dhabi|sharjah|ajman", "United Arab Emirates"), (r"ksa|riyadh|jeddah|dammam|khobar|makkah", "Saudi Arabia"), (r"doha", "Qatar"), (r"manama", "Bahrain"), (r"muscat", "Oman"),
  (r"cairo|alexandria|giza", "Egypt"), (r"tunis", "Tunisia"), (r"amman", "Jordan"), (r"casablanca|rabat", "Morocco"), (r"rome|milan", "Italy"), (r"stockholm", "Sweden"),
  (r"uk|london|manchester", "United Kingdom"), (r"berlin|munich|hamburg", "Germany"), (r"amsterdam|utrecht|rotterdam|the hague", "Netherlands"), (r"barcelona|madrid", "Spain"),
  (r"dublin", "Ireland"), (r"warsaw|krakow", "Poland"), (r"lisbon|porto", "Portugal"), (r"paris|lyon", "France"), (r"brussels", "Belgium"), (r"zurich|geneva", "Switzerland"),
  (r"sydney|melbourne|brisbane|perth|adelaide|canberra", "Australia"), (r"auckland|wellington|christchurch", "New Zealand"), (r"toronto|vancouver|montreal|ottawa|calgary|waterloo", "Canada"),
  (r"tokyo|osaka", "Japan"), (r"sofia", "Bulgaria"), (r"singapore", "Singapore"), (r"usa|new york|san francisco|boston|seattle|austin", "United States of America"),
  (r"bangalore|bengaluru|mumbai|delhi|hyderabad", "India"), (r"lagos|abuja", "Nigeria"), (r"nairobi", "Kenya"), (r"istanbul|ankara", "Turkey"), (r"karachi|lahore|islamabad", "Pakistan")]
_world = ROOT / "dashboard" / "world.json"
WORLD = [c["name"] for c in json.loads(_world.read_text(encoding="utf-8"))] if _world.exists() else []
ALIASES += [(r"johannesburg|cape town|pretoria|durban|stellenbosch", "South Africa"), (r"accra", "Ghana"), (r"kigali", "Rwanda"), (r"addis ababa", "Ethiopia"),
  (r"kampala", "Uganda"), (r"dar es salaam", "Tanzania"), (r"dakar", "Senegal"), (r"algiers", "Algeria"), (r"monterrey|guadalajara", "Mexico"), (r"buenos aires", "Argentina"),
  (r"s[aã]o paulo|rio de janeiro", "Brazil"), (r"bogot[aá]|medell[ií]n", "Colombia"), (r"montevideo", "Uruguay"), (r"almaty|astana", "Kazakhstan"), (r"tashkent", "Uzbekistan"),
  (r"kuala lumpur", "Malaysia"), (r"manila|makati|taguig", "Philippines"), (r"jakarta", "Indonesia"), (r"pune|chennai", "India"), (r"colombo", "Sri Lanka"), (r"dhaka", "Bangladesh"),
  (r"ho chi minh|hanoi", "Vietnam"), (r"bangkok", "Thailand"), (r"taipei", "Taiwan"), (r"seoul", "South Korea"), (r"tbilisi", "Georgia"), (r"yerevan", "Armenia"),
  (r"t[uü]rkiye|izmir", "Turkey"), (r"beirut", "Lebanon"), (r"erbil", "Iraq"), (r"athens", "Greece"), (r"zagreb", "Croatia"), (r"copenhagen", "Denmark"), (r"ljubljana", "Slovenia"),
  (r"helsinki", "Finland"), (r"limassol|nicosia", "Cyprus"), (r"belgrade", "Serbia"), (r"bucharest", "Romania"), (r"czech republic|prague", "Czechia"), (r"vienna", "Austria"),
  (r"oslo", "Norway"), (r"tallinn", "Estonia"), (r"vilnius", "Lithuania"), (r"riga", "Latvia"), (r"budapest", "Hungary"), (r"kyiv", "Ukraine"), (r"wroc[lł]aw|krak[oó]w", "Poland"),
  (r"m[uü]nchen|frankfurt|cologne", "Germany"), (r"oxford|cambridge|edinburgh", "United Kingdom"), (r"cork|galway", "Ireland"), (r"z[uü]rich|basel|lausanne", "Switzerland"),
  (r"turin", "Italy"), (r"braga", "Portugal"), (r"united states|chicago|los angeles|denver|atlanta", "United States of America")]
PLACES = [(re.escape(n.lower()), n) for n in sorted(WORLD, key=len, reverse=True)] + ALIASES
def place(text):
    """The map's country, named exactly as in the world shapes. Empty when the text names no country.
    Ignores an "applied from ..." note, and picks the country named first in the text."""
    s = re.split(r"applied from|apply from|candidate based in", (text or "").lower())[0]
    best = None
    for pat, name in PLACES:
        m = re.search(r"(?<![a-z])(" + pat + r")(?![a-z])", s)
        if m and (best is None or m.start() < best[0]): best = (m.start(), name)
    return best[1] if best else ""
def country(loc):
    return place(loc) or ("Remote" if re.search(r"remote|emea|worldwide|anywhere", loc or "", re.I) else "Other")
def channel(c):
    c = (c or "").lower()
    if "linkedin-message" in c: return "LinkedIn message"
    if "general-email" in c: return "General email"
    if "linkedin" in c: return "LinkedIn Easy Apply"
    for k in ["greenhouse","lever","ashby","workable","smartrecruiters","teamtailor","recruitee","breezy","dover","indeed","glassdoor","bayt","gulftalent","naukrigulf","wuzzuf","email"]:
        if k in c: return k.capitalize() if k not in ("smartrecruiters",) else "SmartRecruiters"
    return "Company site"
import datetime, os
def iso_utc(ts): return datetime.datetime.fromtimestamp(ts, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
def local_day(ts): return datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
def applied_at(r):
    """When the application went in: the log line's own "at", else when its report.md was created (same day only)."""
    if r.get("at"): return r["at"]
    rep = ROOT / r.get("report", "") if r.get("report") else None
    if rep and rep.is_file():
        st = os.stat(rep); t = getattr(st, "st_birthtime", st.st_mtime)
        if local_day(t) == r.get("date"): return iso_utc(t)
    return ""
def replied_at(x):
    """When the email arrived: the line's own "at", else the time inside its Gmail message or thread id (same day only)."""
    if x.get("at"): return x["at"]
    g, th = x.get("gmail", "") or "", x.get("thread", "") or ""
    m = re.search(r"msg-f:(\d+)", g) or re.search(r"thread-f:(\d+)", g)
    ms = int(m.group(1)) >> 20 if m else (int(th, 16) >> 20 if re.fullmatch(r"[0-9a-f]{16}", th) else None)
    if ms and local_day(ms / 1000) == x.get("date"): return iso_utc(ms / 1000)
    return ""
rows, seen, json_lines = [], set(), []
for line in (ROOT/"tracker"/"applied_log.jsonl").read_text(encoding="utf-8").splitlines():
    try: r = json.loads(line)
    except Exception: continue
    json_lines.append(r)
    key = (r.get("company","").strip().lower(), r.get("title","").strip().lower())
    if not r.get("url") or key in seen: continue
    seen.add(key)
    title = r.get("title","")
    rows.append({"date": r.get("date",""), "at": applied_at(r), "company": r.get("company",""), "role": title,
        "location": r.get("location",""), "country": country(r.get("location","")), "map": place(r.get("location","")) or "Remote",
        "channel": channel(r.get("channel","")), "cv": pathlib.Path(r.get("cv","")).name or r.get("cv",""),
        "track": pathlib.Path(r.get("cv","")).stem or "Other",
        "salary_given": r.get("salary_given","") or "", "status": r.get("status","applied"), "url": r.get("url","")})
def section(md, *names):
    for n in names:
        m = re.search(r"^##\s*" + re.escape(n) + r"[^\n]*\n(.*?)(?=^##\s|\Z)", md, re.M | re.S | re.I)
        if m: return m.group(1).strip()
    return ""
def detag(t):
    t = re.sub(r"(?i)<\s*li[^>]*>", "\n- ", t or "")
    t = re.sub(r"(?i)</?\s*(p|h[1-6]|ul|ol|li|br|div|tr|table)\b[^>]*>", "\n", t)
    t = re.sub(r"</?[a-zA-Z][^>]*>", "", t)
    for a, b in (("&amp;", "&"), ("&nbsp;", " "), ("&lt;", "<"), ("&gt;", ">"), ("&#39;", "'"), ("&quot;", '"')): t = t.replace(a, b)
    return re.sub(r"\n\s*\n+", "\n\n", t).strip()
def qa_rows(md):
    body = section(md, "Questions asked")
    out = []
    for line in body.splitlines():
        if not line.strip().startswith("|"): continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or set(cells[0]) <= set("-: ") or cells[0].lower() == "question": continue
        out.append({"q": cells[0], "a": " | ".join(cells[1:])})
    return out
REPORT_OF = {}
for x in json_lines: REPORT_OF.setdefault(x.get("url"), x.get("report", ""))  # first log line per URL
for r in rows:
    rep = REPORT_OF.get(r["url"], "")
    md = (ROOT / rep).read_text(encoding="utf-8") if rep and (ROOT / rep).exists() else ""
    r["cv_label"] = r["cv"]
    r["summary"] = section(md, "What the job is about")[:1500]
    r["jd"] = detag(section(md, "Job description"))[:8000]
    r["qa"] = qa_rows(md)
    letter = section(md, "Cover letter")
    r["letter"] = "" if letter.lower().startswith("none") else letter[:4000]
    r["prep"] = section(md, "Interview prep")[:1500]
rows.sort(key=lambda r: r["at"] or r["date"], reverse=True)
paused = []
for line in (ROOT/"tracker"/"needs_me.md").read_text(encoding="utf-8").splitlines():
    if not line.startswith("| 20"): continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 4: continue
    url = re.findall(r"https?://\S+", cells[2])
    blocker = re.sub(r"\s+", " ", cells[3])
    up = blocker.upper()
    state = "Sent" if up.startswith("DONE") else "Queued" if up.startswith("QUEUED") else "Skipped" if up.startswith("SKIPPED") else "Waiting"
    if state == "Sent": continue  # submitted jobs live under Applications, not the waiting list
    blocker = re.sub(r"^(DONE|QUEUED|SKIPPED)[^:]*:\s*", "", blocker, flags=re.I)
    job = re.sub(r"\s*BLOCKED-CAPTCHA:?\s*", " ", cells[1]).strip()
    paused.append({"date": cells[0], "job": job, "url": url[0].rstrip(";,") if url else "", "state": state, "reason": blocker[:320]})
# ---- PUBLIC-SAFE: the owner may share the dashboard, so private details never reach it.
PRIVATE_Q = re.compile(r"phone|mobile|whatsapp|e-?mail|salary|compensation|package|remuneration|wage|income|\bearn|\bexpect|\bctc\b|\bpay\b|rate|currency|current (company|employer|job|title)|employ|notice|join|start date|nationality|citizen|iqama|visa|sponsor|authori[sz]|gender|\bage\b|birth|marital|military|gpa|grade|reference|address|city|location|linkedin|github|portfolio|website|passport|\bid\b|name", re.I)
PHONE = re.compile(r"\+?\d[\d\s\-()]{7,}\d")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
MONEY = re.compile(r"(?i)(sar|aed|qar|kwd|bhd|omr|egp|tnd|usd|eur|gbp|cad|\$|€|£)\s?[\d,.]+k?|[\d,.]+\s?k?\s?(sar|aed|qar|kwd|bhd|omr|egp|tnd|usd|eur|gbp|cad|aud|inr|dirhams?|riyals?|dinars?|pounds?|dollars?|euros?|rupees?)\b")
MONEY_NAMED = re.compile(r"(?i)\d[\d,.]*\s?k?[,\s]+(?:[a-z]+\s+){0,3}(dirhams?|riyals?|dinars?|pounds?|dollars?|euros?|rupees?|francs?|kron[aeo]r?|yen|yuan|pesos?|lira|rand|naira|shillings?)\b")  # e.g. "12000, United Arab Emirates Dirham"
_terms = ROOT / "config" / "private_terms.txt"
TERMS = [t.strip() for t in _terms.read_text(encoding="utf-8").splitlines() if t.strip() and not t.startswith("#")] if _terms.exists() else []
def term_rx(t):
    """The term, case-insensitive. A figure or phone number also matches with other separators or none (12,000 = 12000)."""
    if sum(c.isdigit() for c in t) >= 4 and re.fullmatch(r"[\d\s,.+\-()]+", t):
        return re.compile(r"(?<!\d)" + r"[\s,.\-()]*".join(re.sub(r"\D", "", t)) + r"(?!\d)")
    return re.compile(re.escape(t), re.I)
TERM_RX = [term_rx(t) for t in TERMS]
def scrub(s):
    s = EMAIL.sub("[email]", s or ""); s = PHONE.sub("[phone]", s); s = MONEY.sub("[amount]", s); s = MONEY_NAMED.sub("[amount]", s)
    for rx in TERM_RX: s = rx.sub("[private]", s)
    return s
for r in rows:
    r.pop("salary_given", None)
    r["qa"] = [{"q": x["q"], "a": "(kept private, see your report)" if PRIVATE_Q.search(x["q"]) else scrub(x["a"])} for x in r.get("qa", [])]
    for k in ("letter", "prep", "summary", "jd"): r[k] = scrub(r.get(k, ""))
for p_ in paused: p_["reason"] = scrub(p_["reason"]); p_["job"] = scrub(p_["job"])
# ---- EMPLOYER REPLIES: tracker/replies.jsonl holds the private record (with Gmail links); only a scrubbed copy goes public.
URL = re.compile(r"https?://\S+|www\.\S+")
def public_text(t): return scrub(URL.sub("", t or "")).strip()
def norm(t): return re.sub(r"[^a-z0-9؀-ۿ]+", "", (t or "").lower())
def spaced(t): return " " + " ".join(re.findall(r"[a-z0-9\u0600-\u06ff]+", (t or "").lower())) + " "
def words(t): return set(re.findall(r"[a-z0-9]+", (t or "").lower()))
def match_row(reply):
    c = spaced(reply.get("company")); hits = []
    if len(c) < 5: return None
    for row in rows:
        rc = spaced(row["company"])
        if len(rc) >= 5 and (c in rc or rc in c): hits.append(row)  # whole words only
    if not hits: return None
    w = words(reply.get("role")) or words(reply.get("subject"))
    best = max(hits, key=lambda row: len(w & words(row["role"])))
    return best if (len(hits) == 1 or w & words(best["role"])) else None
public_replies, rp = [], ROOT/"tracker"/"replies.jsonl"
for r in rows: r["replies"] = []
for i, line in enumerate(rp.read_text(encoding="utf-8").splitlines() if rp.exists() else []):
    try: x = json.loads(line)
    except Exception: continue
    row = match_row(x)
    if row and x.get("date", "") < row["date"]: row = None  # the reply is older than our application, so it answers an earlier one
    said = re.search(r"position at .{1,120}? in ([^.]{3,80})\.", x.get("text", "") or "")  # LinkedIn's decision emails name the job's place
    where = row["map"] if row else place(x.get("role", "")) or place(said.group(1) if said else "")
    pub = {"id": str(i), "date": x.get("date", ""), "at": replied_at(x), "map": where, "company": x.get("company", ""), "role": x.get("role", ""), "outcome": x.get("outcome", "received"),
           "reason": public_text(x.get("reason", "")), "subject": public_text(x.get("subject", "")), "text": public_text(x.get("text", ""))[:1500],
           "source": "agent" if row else "you", "app_url": row["url"] if row else ""}
    public_replies.append(pub)
    if row: row["replies"].append({k: pub[k] for k in ("date", "at", "outcome", "reason", "subject", "text")})
for r in rows:
    r["replies"].sort(key=lambda x: x["at"] or x["date"], reverse=True)
    decided = [x for x in r["replies"] if x["outcome"] != "received"]
    if decided: r["status"] = decided[0]["outcome"]
known = {(x["company"].split()[0].lower(), x["role"].lower()): x["map"] for x in public_replies if x["map"] and x["map"] != "Remote" and x["outcome"] == "rejected" and x["company"].split()}
for x in public_replies:  # the same rejection can arrive twice, and only one may name the place
    if not x["map"] and x["outcome"] == "rejected" and x["company"].split(): x["map"] = known.get((x["company"].split()[0].lower(), x["role"].lower()), "")
public_replies.sort(key=lambda x: x["at"] or x["date"], reverse=True)
def write_json(path, data):  # only rewritten when the bytes change, so repeated runs report no change
    text = json.dumps(data, ensure_ascii=False, indent=0)
    if not path.exists() or path.read_text(encoding="utf-8") != text: path.write_text(text, encoding="utf-8")
write_json(ROOT/"dashboard"/"replies.json", public_replies)
print(len(public_replies), "replies;", sum(x["outcome"] == "rejected" for x in public_replies), "rejected;", sum(bool(r["replies"]) for r in rows), "applications with a reply")
write_json(ROOT/"dashboard"/"applications.json", rows)
write_json(ROOT/"dashboard"/"paused.json", paused)
print(len(rows), "applications;", len(paused), "paused rows")
from collections import Counter
print(Counter(r["country"] for r in rows)); print(Counter(r["channel"] for r in rows))
# ---- STERLING'S NOTE (optional): the pre-written card at the top of the dashboard, rebuilt from the public files above.
try: _sterling = json.loads((ROOT/"config"/"pages.json").read_text(encoding="utf-8")).get("sterling")
except Exception: _sterling = False
if _sterling:
    import subprocess, sys
    _b = subprocess.run([sys.executable, "-I", str(ROOT/"scripts"/"sterling_brief.py")], capture_output=True, text=True)
    print(_b.stdout.strip() or ("briefing failed: " + _b.stderr.strip()[-300:]))
