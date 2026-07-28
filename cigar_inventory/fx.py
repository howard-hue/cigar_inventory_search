from __future__ import annotations

from decimal import Decimal
from typing import Any
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError
import time

from cigar_inventory.http_util import get_json


FRANKFURTER_LATEST = "https://api.frankfurter.app/latest"


# 备用汇率
# 作用：API挂掉时保证任务继续运行
FALLBACK_RATES = {
    "EUR": Decimal("7.85"),
    "CHF": Decimal("8.20"),
    "USD": Decimal("7.20"),
}


def fetch_rate_to_cny(
    from_currency: str,
) -> tuple[Decimal, str, dict[str, Any]]:
    """
    返回:
    (1单位外币=CNY, 日期, 原始JSON)

    使用固定汇率（避免API请求失败）
    """

    cur = from_currency.strip().upper()

    if cur == "CNY":
        return Decimal("1"), "", {}

    if cur in FALLBACK_RATES:
        return (
            FALLBACK_RATES[cur],
            "fixed",
            {},
        )

    raise RuntimeError(
        f"未知货币 {cur}，请在 FALLBACK_RATES 中添加汇率"
    )



def format_fx_note(
    from_currency: str,
    rate: Decimal,
    fx_date: str
) -> str:

    cur = from_currency.upper()

    if cur == "CNY":
        return "基准货币为 CNY"


    d = (
        f" ({fx_date})"
        if fx_date
        else ""
    )

    return (
        f"1 {cur} = {rate} CNY{d}"
    )
