from __future__ import annotations

import os
import requests


def send_text(message: str) -> None:
    """
    发送飞书机器人文本消息
    """

    webhook = os.getenv("FEISHU_WEBHOOK")

    if not webhook:
        print("未配置 FEISHU_WEBHOOK")
        return

    payload = {
        "msg_type": "text",
        "content": {
            "text": message
        }
    }

    r = requests.post(
        webhook,
        json=payload,
        timeout=20,
    )

    print(f"飞书返回：{r.status_code}")

    if r.status_code != 200:
        print(r.text)
