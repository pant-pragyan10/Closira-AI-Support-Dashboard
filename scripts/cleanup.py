"""
Simple cleanup utility to remove logs and temporary files before packaging.
Run: python scripts/cleanup.py
"""
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
BUILD_DIRS = [ROOT / "dist", ROOT / "build"]


def remove_logs():
    if LOG_DIR.exists():
        print(f"Removing logs at {LOG_DIR}")
        shutil.rmtree(LOG_DIR)
    else:
        print("No logs/ directory found.")


def remove_builds():
    for d in BUILD_DIRS:
        if d.exists():
            print(f"Removing {d}")
            shutil.rmtree(d)


def main():
    remove_logs()
    remove_builds()
    print("Cleanup complete. Review .gitignore to ensure logs aren't committed.")


if __name__ == "__main__":
    main()
