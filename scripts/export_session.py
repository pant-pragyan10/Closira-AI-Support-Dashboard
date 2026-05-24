"""Export session data and logs for packaging or CRM ingestion.

Usage:
    python scripts/export_session.py --out exported_sessions.json
"""
import json
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"


def gather_sessions():
    sessions = []
    if not LOG_DIR.exists():
        print("No logs/ directory found — nothing to export.")
        return sessions
    for p in LOG_DIR.glob("**/*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            sessions.append({"path": str(p.relative_to(ROOT)), "data": data})
        except Exception:
            # skip malformed logs
            continue
    return sessions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="exported_sessions.json")
    args = parser.parse_args()
    sessions = gather_sessions()
    out_path = Path(args.out)
    out_path.write_text(json.dumps(sessions, indent=2), encoding="utf-8")
    print(f"Wrote {len(sessions)} sessions to {out_path}")


if __name__ == "__main__":
    main()
