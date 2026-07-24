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

    优先使用 Frankfurter
    失败使用备用汇率
    """

    cur = from_currency.strip().upper()

    if cur == "CNY":
        return Decimal("1"), "", {}


    qs = urlencode({
        "from": cur,
        "to": "CNY"
    })

    url = f"{FRANKFURTER_LATEST}?{qs}"


    last_error = None


    # 重试3次
    for attempt in range(3):

        try:

            data = get_json(
                url,
                timeout=10.0
            )


            date = str(
                data.get("date") or ""
            )

            rates = data.get("rates") or {}


            if "CNY" in rates:

                rate = Decimal(
                    str(rates["CNY"])
                )

                return rate, date, data


        except Exception as e:

            last_error = e

            print(
                f"[汇率] {cur} 请求失败 "
                f"第 {attempt+1}/3 次: {e}"
            )

            time.sleep(3)



    # API失败，使用备用
    if cur in FALLBACK_RATES:

        print(
            f"[汇率] 使用备用汇率: "
            f"1 {cur} = {FALLBACK_RATES[cur]} CNY"
        )

        return (
            FALLBACK_RATES[cur],
            "fallback",
            {
                "error": str(last_error)
            }
        )


    raise RuntimeError(
        f"无法获取 {cur}->CNY 汇率: {last_error}"
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
