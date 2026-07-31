from __future__ import annotations
import re
from typing import Any, Iterator
from cigar_inventory.config_loader import SiteConfig
from cigar_inventory.http_util import fetch_text, get_json

CUBAN_BRANDS = [
    'cohiba', 'montecristo', 'partagas', 'romeo', 'h.upmann', 'hoyo',
    'bolivar', 'trinidad', 'punch', 'quai', 'ramon', 'san cristobal',
    'juan lopez', 'diplomaticos', 'por larranaga', 'quintero',
    'rafael', 'vegueros', 'fonseca',
]


def iter_products(site: SiteConfig) -> Iterator[dict[str, Any]]:
    base_url = site.base_url.rstrip('/')
    max_pages = site.max_pages or 50

    for page_num in range(1, max_pages + 1):
        url = f"{base_url}/wp-json/wp/v2/product?per_page=100&page={page_num}"
        try:
            resp_text = fetch_text(url, timeout=20.0)
            import json
            products = json.loads(resp_text)
        except Exception:
            break

        if not products:
            break

        for p in products:
            name_raw = p.get('title', {})
            if isinstance(name_raw, dict):
                title = name_raw.get('rendered', '')
            else:
                title = str(name_raw)

            if not title:
                continue

            title_lower = title.lower()
            brand = ''
            for b in CUBAN_BRANDS:
                if b in title_lower:
                    brand = b.title()
                    break

            if not brand:
                continue

            link = p.get('link', '')

            # 从产品页面获取价格
            price_str = ''
            try:
                page_html = fetch_text(link, timeout=15.0)
                price_match = re.findall(r'class="[^"]*price[^"]*amount[^"]*"[^>]*>([^<]+)', page_html)
                if not price_match:
                    price_match = re.findall(r'"price":"([^"]+)"', page_html)
                if price_match:
                    price_str = price_match[0].replace('\xa0', '').replace('CHF', '').replace(',', '.').strip()
                    price_str = re.sub(r'[^\d.]', '', price_str)
            except:
                pass

            yield {
                'title': title,
                'handle': link.split('/')[-2] if link.endswith('/') else link.split('/')[-1],
                'vendor': brand,
                'tags': [brand], '__cigar_section__': True,
                'product_type': 'cigar',
                'variants': [{'price': price_str or '0', 'available': True}],
                '__product_url__': link,
            }
