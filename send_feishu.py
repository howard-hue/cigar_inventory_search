#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import glob
import json
import os
import urllib.request
from pathlib import Path

WEBHOOK = os.environ.get("FEISHU_WEBHOOK")

if not WEBHOOK:
    raise RuntimeError("FEISHU_WEBHOOK 未配置")


def latest_csv():
    files = sorted(glob.glob("inventory_*.csv"))
    if not files:
        raise RuntimeError("没有找到 inventory_*.csv")
    return files[-1]


csv_file = latest_csv()

rows = []

with open(csv_file, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

site_count = {}

for r in rows:
    site = r["网站"]
    site_count[site] = site_count.get(site, 0) + 1

msg = []

msg.append("📊 雪茄库存扫描完成")
msg.append("")
msg.append(f"商品总数：{len(rows)}")
msg.append("")
msg.append("各网站：")

for site, num in sorted(site_count.items()):
    msg.append(f"• {site}：{num}")

payload = {
    "msg_type": "text",
    "content": {
        "text": "\n".join(msg)
    }
}

req = urllib.request.Request(
    WEBHOOK,
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Content-Type": "application/json"
    }
)

with urllib.request.urlopen(req) as r:
    print(r.read().decode())
