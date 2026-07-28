from __future__ import annotations

import json
from typing import Any

import requests

USER_AGENT = "cigar-inventory-search/0.2 (+configurable inventory check)"

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})


def get_json(url: str, timeout: float = 60.0) -> dict[str, Any]:
    resp = SESSION.get(url, timeout=timeout, headers={"Accept": "application/json"})
    resp.raise_for_status()
    return resp.json()


def get_json_any(url: str, timeout: float = 60.0) -> Any:
    resp = SESSION.get(url, timeout=timeout, headers={"Accept": "application/json"})
    resp.raise_for_status()
    return resp.json()


def post_json(url: str, body: dict[str, Any], timeout: float = 60.0) -> dict[str, Any]:
    resp = SESSION.post(url, json=body, timeout=timeout, headers={"Accept": "application/json"})
    resp.raise_for_status()
    return resp.json()


def fetch_text(url: str, timeout: float = 45.0) -> str:
    resp = SESSION.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def build_url(base: str, path: str, query: dict[str, str] | None = None) -> str:
    from urllib.parse import urlencode
    b = base.rstrip("/")
    p = path if path.startswith("/") else f"/{path}"
    url = f"{b}{p}"
    if query:
        url += "?" + urlencode(query)
    return url
