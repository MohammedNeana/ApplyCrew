# Re-exports the dashboard data and prints which files differ from the last upload.
# "python3 -I scripts/dash_changed.py --mark" records the current files as uploaded.
# Output: "NO CHANGE" or "CHANGED: <files>" (files under dashboard/; each one's dataset id is its name without .json).
# If the self-check fails it prints "SELFCHECK FAILED: ..." and exits 1: then nothing may be uploaded.
import hashlib, json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
FILES = ["applications.json", "paused.json", "replies.json", "briefing.json"]  # briefing.json exists only when Sterling is on
STATE = ROOT / "tracker" / ".dashboard_uploaded.json"
def digests():
    return {f: hashlib.sha256((ROOT / "dashboard" / f).read_bytes()).hexdigest() for f in FILES if (ROOT / "dashboard" / f).exists()}
if "--mark" in sys.argv:
    STATE.write_text(json.dumps(digests()))
    sys.exit()
for script in ["export_dashboard.py", "build_index.py"]:
    subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / script)], check=True, capture_output=True)
subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / "live_pages.py"), "--build-only"], capture_output=True)  # Sterling's data first
check = subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / "selfcheck.py")], capture_output=True, text=True)
if check.returncode != 0:
    print(check.stdout.strip() or "SELFCHECK FAILED: " + check.stderr.strip()[-300:])
    sys.exit(1)
old = json.loads(STATE.read_text()) if STATE.exists() else {}
changed = [f for f, h in digests().items() if old.get(f) != h]
print("CHANGED: " + " ".join(changed) if changed else "NO CHANGE")
