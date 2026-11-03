# Re-exports the dashboard data and prints which files differ from the last upload.
# "python3 -I scripts/dash_changed.py --mark" records the current files as uploaded.
import hashlib, json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
FILES = ["applications.json", "paused.json", "replies.json"]
STATE = ROOT / "tracker" / ".dashboard_uploaded.json"
def digests():
    return {f: hashlib.sha256((ROOT / "dashboard" / f).read_bytes()).hexdigest() for f in FILES}
if "--mark" in sys.argv:
    STATE.write_text(json.dumps(digests()))
    sys.exit()
for script in ["export_dashboard.py", "build_index.py"]:
    subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / script)], check=True, capture_output=True)
old = json.loads(STATE.read_text()) if STATE.exists() else {}
changed = [f for f, h in digests().items() if old.get(f) != h]
print("CHANGED: " + " ".join(changed) if changed else "NO CHANGE")
