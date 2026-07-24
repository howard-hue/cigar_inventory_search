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


def _is_product_url(
    loc: str,
    base_netloc: str
) -> bool:

    try:
        u = urlparse(loc)

    except Exception:
        return False


    if u.netloc != base_netloc:
        return False


    path = (u.path or "").lower()


    # 静态资源过滤

    if path.endswith(
        (
            ".jpg",
            ".png",
            ".jpeg",
            ".gif",
            ".webp",
            ".svg",
            ".css",
            ".js",
        )
    ):
        return False


    # 后台/搜索/购物车过滤

    exclude_words = [
        "/category",
        "/categories",
        "/manufacturer",
        "/brand",
        "/brands",
        "/search",
        "/login",
        "/cart",
        "/checkout",
        "/account",
    ]


    for word in exclude_words:

        if word in path:
            return False



    parts = [
        x for x in path.strip("/").split("/")
        if x
    ]


    # 空路径
    if len(parts) < 1:
        return False



    # Prestashop 商品判断

    if ".html" in path:
        return True


    if "/product/" in path:
        return True


    if re.search(
        r"/\d+-",
        path
    ):
        return True


    return False



def iter_products(
    site: SiteConfig
) -> Iterator[dict[str, Any]]:


    base = site.base_url.rstrip("/")

    netloc = urlparse(base).netloc


    max_items = int(
        site.adapter_options.get(
            "max_scrape_products"
        ) or 280
    )


    # =========================
    # sitemap 获取
    # =========================

    sitemap_candidates = []


    custom = site.adapter_options.get(
        "sitemap_url"
    )


    if custom:
        sitemap_candidates.append(custom)



    sitemap_candidates.extend(
        [
            f"{base}/sitemap.xml",
            f"{base}/sitemap_index.xml",
            f"{base}/1_index_sitemap.xml",
            f"{base}/sitemap.xml.gz",
            f"{base}/modules/gsitemap/sitemap.xml",
            f"{base}/modules/gsitemap/sitemap-1.xml",
            f"{base}/modules/gsitemap/sitemap-products.xml",
            f"{base}/en/sitemap.xml",
            f"{base}/it/sitemap.xml",
        ]
    )


    xml = None
    used = None



    for sm in sitemap_candidates:

        try:

            print(
                f"[{site.display_name}] 尝试 sitemap: {sm}"
            )


            xml = fetch_text(
                sm,
                timeout=60
            )


            used = sm

            break


        except Exception as e:

            print(
                f"[{site.display_name}] sitemap失败: {e}"
            )



    locs = []



    # =========================
    # 没有 sitemap
    # 首页扫描
    # =========================

    if xml is None:


        print(
            f"[{site.display_name}] 无 sitemap，尝试首页扫描"
        )


        try:

            home_html = fetch_text(
                base,
                timeout=60
            )


        except Exception as e:

            print(
                f"[{site.display_name}] 首页读取失败: {e}"
            )

            return



        links = re.findall(
            r'href=["\']([^"\']+)["\']',
            home_html,
            re.I
        )


        for link in links:


            if link.startswith("/"):

                link = base + link



            try:

                if _is_product_url(
                    link,
                    netloc
                ):

                    locs.append(link)


            except Exception:

                continue



        print(
            f"[{site.display_name}] 首页发现商品候选URL: {len(locs)}"
        )



    else:


        print(
            f"[{site.display_name}] 使用 sitemap: {used}"
        )


        locs = parse_sitemap_locs(xml)


        print(
            f"[{site.display_name}] sitemap URL数量: {len(locs)}"
        )



        # sitemap index

        if (
            not locs
            and "<sitemapindex" in xml.lower()
        ):


            try:

                root = ET.fromstring(xml)


            except ET.ParseError:

                return



            ns = {
                "sm":
                "http://www.sitemaps.org/schemas/sitemap/0.9"
            }



            children = []


            for e in root.findall(
                ".//sm:loc",
                ns
            ):

                if e.text:

                    children.append(
                        e.text.strip()
                    )



            print(
                f"[{site.display_name}] 子sitemap数量: {len(children)}"
            )



            for child in children:


                try:

                    sub_xml = fetch_text(
                        child,
                        timeout=60
                    )


                    locs.extend(
                        parse_sitemap_locs(
                            sub_xml
                        )
                    )


                except Exception as e:

                    print(
                        f"[{site.display_name}] 子sitemap失败: {e}"
                    )



    print(
        f"[{site.display_name}] 最终URL数量: {len(locs)}"
    )



    # =========================
    # 抓商品
    # =========================

    seen = set()

    count = 0



    for loc in locs:


        if count >= max_items:
            break



        if not _is_product_url(
            loc,
            netloc
        ):

            continue



        if loc in seen:

            continue



        seen.add(loc)



        try:

            html = fetch_text(
                loc,
                timeout=35
            )


        except Exception:

            continue



        # 标题

        title_m = re.search(
            r"<h1[^>]*>(.*?)</h1>",
            html,
            re.I | re.S
        )


        if title_m:

            title = re.sub(
                "<.*?>",
                "",
                title_m.group(1)
            ).strip()

        else:

            title = loc.split("/")[-1]



        price_s = "0"

        available = True



        # JSON-LD价格

        for ld in extract_json_ld_products(html):


            got = price_from_ld_product(ld)


            if got:

                price_s, available = got

                break



        # meta价格备用

        if price_s == "0":


            pm = re.search(
                r'property="product:price:amount"\s+content="([\d.]+)"',
                html,
                re.I
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



        if not is_cuban_cigar_product({
            "title": title,

            "vendor": "",

            "tags": ["cigar"],
        }):
            continue


       count += 1
       print(
           f"[{site.display_name}] 商品 {count}: {title}"
       )




        yield {

            "title": title,

            "handle": loc[-120:],

            "body_html": "",

            "vendor": "",

            "product_type": "PrestaShop",

            "tags": [
                "cigar"
            ],

            "__cigar_section__": True,

            "variants": [
                variant
            ],

            "__product_url__": loc,

        }



    print(
        f"[{site.display_name}]完成 商品数:{count}"
    )
