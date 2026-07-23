from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

DATA_DIR = Path("data")

LATEST_FILE = DATA_DIR / "latest.json"

PREVIOUS_FILE = DATA_DIR / "previous.json"


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_latest() -> list[dict[str, Any]]:
    if not LATEST_FILE.exists():
        return []

    with open(LATEST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_previous() -> list[dict[str, Any]]:
    if not PREVIOUS_FILE.exists():
        return []

    with open(PREVIOUS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def rotate_latest() -> None:
    """
    latest -> previous
    """

    ensure_data_dir()

    if LATEST_FILE.exists():
        PREVIOUS_FILE.write_text(
            LATEST_FILE.read_text(encoding="utf-8"),
            encoding="utf-8",
        )


def save_latest(rows) -> None:
    """
    保存最新库存
    """

    ensure_data_dir()

    data = []

    for r in rows:

        if hasattr(r, "__dataclass_fields__"):
            d = asdict(r)
        else:
            d = dict(r)

        data.append(d)

    with open(LATEST_FILE, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )
