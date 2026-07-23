import os
import json
import requests


def send_new_products(products):

    if not products:
        return

    webhook = os.environ.get("FEISHU_WEBHOOK")

    if not webhook:
        print("没有配置 FEISHU_WEBHOOK")
        return

    elements = []

    elements.append({
        "tag": "markdown",
        "content": f"## 🎉 检测到 **{len(products)}** 个新品"
    })

    for item in products[:10]:

        elements.append({
            "tag": "hr"
        })

        elements.append({
            "tag": "markdown",
            "content":
                f"**{item['产品名称']}**\n\n"
                f"🏪 {item['网站']}\n\n"
                f"💰 ¥{item['人民币税后']}"
        })

        elements.append({
            "tag": "action",
            "actions": [
                {
                    "tag": "button",
                    "text": {
                        "tag": "plain_text",
                        "content": "打开商品"
                    },
                    "url": item["链接"],
                    "type": "primary"
                }
            ]
        })

    body = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "template": "green",
                "title": {
                    "tag": "plain_text",
                    "content": "雪茄上新通知"
                }
            },
            "elements": elements
        }
    }

    r = requests.post(webhook, json=body, timeout=20)

    print(r.status_code)
    print(r.text)
