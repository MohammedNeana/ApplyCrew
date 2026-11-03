# Tracks email ids the inbox check has already handled.
# "python3 -I scripts/inbox_seen.py id id ..." prints the ids not handled yet.
# "python3 -I scripts/inbox_seen.py --mark id id ..." records them as handled.
import pathlib, sys
SEEN = pathlib.Path(__file__).resolve().parent.parent / "tracker" / ".inbox_seen.txt"
seen = set(SEEN.read_text().split()) if SEEN.exists() else set()
args = sys.argv[1:]
if args[:1] == ["--mark"]:
    SEEN.write_text("\n".join(sorted(seen | set(args[1:]))) + "\n")
else:
    new = [a for a in args if a not in seen]
    print("NEW: " + " ".join(new) if new else "NOTHING NEW")
