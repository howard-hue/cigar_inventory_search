from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any


@dataclass
class ChangeResult:
    new: list[dict[str, Any]]
    removed: list[dict[str, Any]]
    price_changed: list[dict[str, Any]]
    back_in_stock: list[dict[str, Any]]


def make_key(item: dict[str, Any]) -> str:
    """
    商品唯一ID
    网站 + 产品名称 + 规格
    """

    return "|".join(
        [
            str(item.get("网站", "")).strip(),
            str(item.get("产品名称", "")).strip(),
            str(item.get("规格", "")).strip(),
        ]
    )


def price(item: dict[str, Any]) -> Decimal:
    """
    返回人民币税后价格
    """

    value = item.get("人民币税后", "0")

    try:
        return Decimal(str(value))
    except Exception:
        return Decimal("0")


def build_index(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """
    建立 Key -> 商品 的索引
    """

    result = {}

    for item in items:
        result[make_key(item)] = item

    return result


def compare(
    previous: list[dict[str, Any]],
    latest: list[dict[str, Any]],
) -> ChangeResult:

    previous_map = build_index(previous)
    latest_map = build_index(latest)

    previous_keys = set(previous_map.keys())
    latest_keys = set(latest_map.keys())

    # 新增
    new = [
        latest_map[k]
        for k in sorted(latest_keys - previous_keys)
    ]

    # 下架
    removed = [
        previous_map[k]
        for k in sorted(previous_keys - latest_keys)
    ]

    # 价格变化
    price_changed = []

    for key in sorted(previous_keys & latest_keys):

        old_item = previous_map[key]
        new_item = latest_map[key]

        old_price = price(old_item)
        new_price = price(new_item)

        if old_price != new_price:

            diff = new_price - old_price

            item = dict(new_item)

            item["旧价格"] = str(old_price)
            item["新价格"] = str(new_price)
            item["价格变化"] = str(diff)

            if diff < 0:
                item["变化类型"] = "降价"
            else:
                item["变化类型"] = "涨价"

            price_changed.append(item)

    return ChangeResult(
        new=new,
        removed=removed,
        price_changed=price_changed,
        back_in_stock=[],
    )


