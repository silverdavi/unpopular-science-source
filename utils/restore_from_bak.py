#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
import shutil


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    allowed_exts = {".tex", ".md", ".py", ".txt", ".sh", ".svg", ".opf"}

    replaced: list[Path] = []

    for bak_path in repo_root.rglob("*.bak"):
        target = bak_path.with_suffix("")  # strip .bak to get original
        if target.suffix.lower() not in allowed_exts:
            continue

        # Ensure parent directory exists (it should)
        target.parent.mkdir(parents=True, exist_ok=True)

        # Copy .bak over the target (create or overwrite)
        shutil.copy2(str(bak_path), str(target))
        replaced.append(target)

    # Write summary file at repo root
    summary_file = repo_root / "replaced_files.txt"
    summary_file.write_text("\n".join(str(p) for p in replaced))

    print(f"Replaced {len(replaced)} files.")
    for p in replaced:
        print(p)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


