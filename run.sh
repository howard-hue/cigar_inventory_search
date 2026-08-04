#!/bin/bash
cd ~/cigar_inventory_search
source venv/bin/activate
unset ALL_PROXY https_proxy http_proxy
export PYTHONHTTPSVERIFY=0
export FEISHU_WEBHOOK="https://open.feishu.cn/open-apis/bot/v2/hook/b1ee3bb8-e592-4e04-9625-2ea51d6202a0"
rm -f inventory_*.csv inventory_*.html
python3 run_inventory.py
python3 -m notifier.main
