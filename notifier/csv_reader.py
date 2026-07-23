from __future__ import annotations

import csv
from pathlib import Path


def load_csv(path: Path) -> list[dict]:
    """
    读取 inventory_xxx.csv
    """

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        reader = csv.DictReader(f)

        return list(reader)
