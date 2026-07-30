from __future__ import annotations
import re
from typing import Any, Iterator
from cigar_inventory.config_loader import SiteConfig
from cigar_inventory.http_util import fetch_text


def iter_products(site: SiteConfig) -> Iterator[dict[str, Any]]:
    base_url = site.base_url.rstrip('/')
    max_pages = site.max_pages or 25

    for page_num in range(1, max_pages + 1):
        url = f"{base_url}/it/170-cubani-habanos?page={page_num}"
        try:
            html = fetch_text(url, timeout=20.0)
        except Exception:
            break

        products = re.findall(
            r'<h[23][^>]*>\s*<a[^>]*href="([^"]*?)"[^>]*>([^<]+)',
            html
        )

        if not products:
            break

        prices = re.findall(
            r'class="[^"]*price[^"]*"[^>]*>([^<]+)',
            html
        )

        clean_prices = []
        for p in prices:
            p = p.strip().replace('\xa0', ' ').replace('CHF', '').replace(',', '.').strip()
            if p and re.match(r'^\d+\.?\d*$', p):
                clean_prices.append(p)

        for i, (href, title) in enumerate(products):
            title = title.strip()
            if not title:
                continue

            price_str = ""
            if i < len(clean_prices):
                price_str = clean_prices[i]

            brand = ""
            title_lower = title.lower()
            brand_map = {
                'cohiba': 'Cohiba', 'montecristo': 'Montecristo',
                'partagas': 'Partagas', 'romeo': 'Romeo y Julieta',
                'h.upmann': 'H. Upmann', 'hoyo': 'Hoyo de Monterrey',
                'bolivar': 'Bolivar', 'trinidad': 'Trinidad',
                'punch': 'Punch', 'quai': "Quai d'Orsay",
                'ramon': 'Ramon Allones', 'san cristobal': 'San Cristobal',
                'juan lopez': 'Juan Lopez', 'diplomaticos': 'Diplomaticos',
                'por larranaga': 'Por Larranaga', 'quintero': 'Quintero',
                'rafael': 'Rafael Gonzalez', 'vegueros': 'Vegueros',
                'fonseca': 'Fonseca',
            }
            for key, val in brand_map.items():
                if key in title_lower:
                    brand = val
                    break

            if not brand:
                continue

            yield {
                'title': title,
                'handle': href.split('/')[-1].split('#')[0],
                'vendor': brand,
                'tags': [brand], '__cigar_section__': True,
                'variants': [{'price': price_str or '0', 'available': True}],
                '__product_url__': href,
            }
