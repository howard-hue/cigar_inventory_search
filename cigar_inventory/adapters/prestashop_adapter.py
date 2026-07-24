from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any, Iterator
from urllib.parse import urlparse

from cigar_inventory.config_loader import SiteConfig
from cigar_inventory.http_util import fetch_text

from cigar_inventory.adapters.scrape_util import (
    extract_json_ld_products,
    parse_sitemap_locs,
    price_from_ld_product,
)


def _is_product_url(loc: str, base_netloc: str) -> bool:
    try:
        u = urlparse(loc)
    except Exception:
        return False

    if u.netloc != base_netloc:
        return False

    path = (u.path or "").lower()

    # 排除图片
    if path.endswith(
        (".jpg", ".png", ".jpeg", ".gif", ".webp", ".svg")
    ):
        return False

    # 排除明显分类页
    exclude_words = [
        "/category",
        "/categories",
        "/manufacturer",
        "/brand",
        "/brands",
        "/search",
        "/login",
    ]

    for word in exclude_words:
        if word in path:
            return False

    parts = [x for x in path.strip("/").split("/") if x]

    # 太短一般不是商品
    if len(parts) < 2:
        return False

    return True


def iter_products(site: SiteConfig) -> Iterator[dict[str, Any]]:
    base = site.base_url.rstrip("/")
    netloc = urlparse(base).netloc

    max_items = int(
        site.adapter_options.get("max_scrape_products") or 280
    )

    sm_url = str(
        site.adapter_options.get("sitemap_url")
        or f"{base}/sitemap.xml"
    )

    print(f"[{site.display_name}] sitemap: {sm_url}")

    try:
        xml = fetch_text(sm_url, timeout=60.0)

    except Exception as e:
        print(
            f"[{site.display_name}] sitemap读取失败: {e}"
        )
        return


    locs = parse_sitemap_locs(xml)

    print(
        f"[{site.display_name}] sitemap初始URL数量: {len(locs)}"
    )


    # sitemap index
    if not locs and "<sitemapindex" in xml.lower():

        print(
            f"[{site.display_name}] 检测到 sitemap index"
        )

        try:
            root = ET.fromstring(xml)

        except ET.ParseError:
            print(
                f"[{site.display_name}] sitemap XML解析失败"
            )
            return


        ns = {
            "sm": "http://www.sitemaps.org/schemas/sitemap/0.9"
        }

        sitemap_links = []

        for loc_el in root.findall(".//sm:loc", ns):

            if loc_el.text:
                sitemap_links.append(
                    loc_el.text.strip()
                )


        print(
            f"[{site.display_name}] 子sitemap数量: {len(sitemap_links)}"
        )


        for sub_url in sitemap_links:

            try:

                sub_xml = fetch_text(
                    sub_url,
                    timeout=60.0
                )

                sub_locs = parse_sitemap_locs(
                    sub_xml
                )

                locs.extend(sub_locs)


            except Exception as e:

                print(
                    f"[{site.display_name}] 子sitemap失败: {e}"
                )


    print(
        f"[{site.display_name}] 最终URL数量: {len(locs)}"
    )


    seen: set[str] = set()

    count = 0
    checked = 0
    filtered = 0


    for loc in locs:

        if count >= max_items:
            break


        checked += 1


        if checked <= 20:
            print(
                f"[{site.display_name}] 检查URL: {loc}"
            )


        if not _is_product_url(
            loc,
            netloc
        ):

            filtered += 1

            if checked <= 20:
                print(
                    f"[{site.display_name}] 过滤URL"
                )

            continue


        if loc in seen:
            continue


        seen.add(loc)


        try:

            html = fetch_text(
                loc,
                timeout=35.0
            )

        except Exception as e:

            if checked <= 20:
                print(
                    f"[{site.display_name}] 页面读取失败: {e}"
                )

            continue



        title_m = re.search(
            r"<h1[^>]*>([^<]+)</h1>",
            html,
            re.I,
        )


        title = (
            title_m.group(1).strip()
            if title_m
            else loc.rsplit("/", 1)[-1]
        )


        handle = re.sub(
            r"[^\w\-]+",
            "-",
            urlparse(loc)
            .path
            .strip("/")
            .replace("/", "-"),
        )[:120] or "item"


        price_s = "0"
        available = True


        for ld in extract_json_ld_products(html):

            got = price_from_ld_product(ld)

            if got:

                price_s, available = got
                break



        if price_s == "0":

            pm = re.search(
                r'property="product:price:amount"\s+content="([\d.]+)"',
                html,
                re.I,
            )

            if pm:

                price_s = pm.group(1)



        variant = {
            "id": None,
            "title": "Default Title",
            "option1": "默认",
            "option2": None,
            "option3": None,
            "sku": "",
            "price": price_s,
            "available": available,
            "inventory_quantity": None,
        }


        count += 1


        print(
            f"[{site.display_name}] 找到商品 {count}: {title}"
        )


        yield {

            "title": title,
            "handle": handle,
            "body_html": "",
            "vendor": "",
            "product_type": "PrestaShop",
            "tags": ["cigar"],
            "__cigar_section__": True,
            "variants": [
                variant
            ],
            "__product_url__": loc,

        }


    print(
        f"[{site.display_name}] 完成: "
        f"检查{checked} URL, "
        f"过滤{filtered}, "
        f"商品{count}"
    )
