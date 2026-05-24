"""Lightweight transcript runner and validator.

This runner performs dry-run validation of transcript format and expected JSON blocks.
It can be extended to run live evaluations against agents when GROQ_API_KEY is set.
"""
import argparse
import glob
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPTS = ROOT / "test_transcripts"
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)


def extract_expected_json(md_text: str):
    # Find the first ```json ... ``` block after 'Expected JSON Output'
    m = re.search(r"# Expected JSON Output\n\n```json\n(.*?)\n```", md_text, flags=re.S)
    if not m:
        return None
    return m.group(1)


def validate_json_block(json_text: str):
    try:
        obj = json.loads(json_text)
        return True, obj, ""
    except Exception as e:
        return False, None, str(e)


def run_dry():
    results = []
    for md in TRANSCRIPTS.rglob("*.md"):
        txt = md.read_text(encoding="utf-8")
        exp = extract_expected_json(txt)
        ok = False
        err = "no expected json block"
        obj = None
        if exp:
            ok, obj, err = validate_json_block(exp)
        results.append({"file": str(md.relative_to(ROOT)), "ok": ok, "error": err, "expected": obj})
    out = LOGS / "test_results.json"
    out.write_text(json.dumps(results, indent=2))
    print(f"Wrote results to {out}")
    failures = [r for r in results if not r["ok"]]
    print(f"Total: {len(results)}, Failures: {len(failures)}")
    for f in failures:
        print(f"FAIL: {f['file']} - {f['error']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Only validate expected JSON blocks")
    parser.add_argument("--live", action="store_true", help="Run live against agents (not implemented)")
    args = parser.parse_args()

    if args.dry_run:
        run_dry()
    else:
        print("Only --dry-run is supported in this lightweight runner currently.")
