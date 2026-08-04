import re

with open('cigar_inventory/pipeline.py', 'r') as f:
    content = f.read()

# 替换 collect_rows 函数，用并行抓取
old_func = '''def collect_rows(cfg: AppConfig) -> list[ExportRow]:
    rows: list[ExportRow] = []
    enabled = [s for s in cfg.sites if s.enabled]
    currencies = {s.currency.upper() for s in enabled}
    fx_rates = _load_fx_rates(currencies) if currencies else {}

    for site in enabled:
        try:
            for p in iter_normalized_products(site):
                if isinstance(p, dict):
                    _append_rows_for_product(site, cfg, p, fx_rates, rows)
        except ValueError as e:
            print(
                f"[跳过] {site.display_name} ({site.id}): {e}",
                file=sys.stderr,
            )
        except urllib.error.HTTPError as e:
            print(
                f"[跳过] {site.display_name} ({site.id}): HTTP {e.code} {e.reason}",
                file=sys.stderr,
            )
        except urllib.error.URLError as e:
            print(
                f"[跳过] {site.display_name} ({site.id}): 网络错误 {e.reason!r}",
                file=sys.stderr,
            )
        except json.JSONDecodeError as e:
            print(
                f"[跳过] {site.display_name} ({site.id}): JSON 解析失败 ({e})",
                file=sys.stderr,
            )'''

new_func = '''def _fetch_site(site, cfg, fx_rates):
    """单个站点抓取，返回 (site_name, rows, error)"""
    rows = []
    try:
        for p in iter_normalized_products(site):
            if isinstance(p, dict):
                _append_rows_for_product(site, cfg, p, fx_rates, rows)
        return site.display_name, rows, None
    except Exception as e:
        return site.display_name, rows, f"[跳过] {site.display_name} ({site.id}): {e.__class__.__name__}"


def collect_rows(cfg: AppConfig) -> list[ExportRow]:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    rows: list[ExportRow] = []
    enabled = [s for s in cfg.sites if s.enabled]
    currencies = {s.currency.upper() for s in enabled}
    fx_rates = _load_fx_rates(currencies) if currencies else {}

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(_fetch_site, site, cfg, fx_rates): site for site in enabled}
        for future in as_completed(futures):
            site_name, site_rows, error = future.result()
            if error:
                print(error, file=sys.stderr)
            rows.extend(site_rows)

    return rows'''

content = content.replace(old_func, new_func)

with open('cigar_inventory/pipeline.py', 'w') as f:
    f.write(content)

print("已应用并行优化")
