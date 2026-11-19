#!/usr/bin/env python3
"""Copy the pre-rendered poster into the make.fun output folder.

The poster itself lives next to this script as ``entry.png``; this module
only moves those bytes to ``$MAKEFUN_OUTPUT_DIR/entry.png`` (``/output``
when the variable is unset).  Standard library only, no network access,
no clock, no randomness — the output is a byte-for-byte copy every run.
"""

import os
import sys
from pathlib import Path


def locate_source() -> Path:
    """Return the poster file shipped alongside this script."""
    here = Path(__file__).resolve().parent
    poster = here / "entry.png"
    if not poster.is_file():
        raise SystemExit(f"poster not found next to main.py: {poster}")
    return poster


def locate_destination() -> Path:
    """Return the output path, creating the folder when needed."""
    target_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / "entry.png"


def main() -> int:
    source = locate_source()
    destination = locate_destination()
    payload = source.read_bytes()
    if not payload:
        raise SystemExit("poster file is empty, refusing to write output")
    destination.write_bytes(payload)
    print(f"wrote {destination} ({len(payload)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
