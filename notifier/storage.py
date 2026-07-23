from __future__ import annotations

import json
from pathlib import Path


DATA_DIR = Path("data")
LATEST_FILE = DATA_DIR / "latest.json"


def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)


def load_latest() -> list[dict]:
    """
    读取上一次保存的数据
    """

    ensure_data_dir()

    if not LATEST_FILE.exists():
        return []

    with LATEST_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_latest(rows: list[dict]) -> None:
    """
    保存最新扫描结果
    """

    ensure_data_dir()

    with LATEST_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            rows,
            f,
            ensure_ascii=False,
            indent=2,
        )
