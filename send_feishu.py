import json
import os
import urllib.request

WEBHOOK = os.environ.get("FEISHU_WEBHOOK")

if not WEBHOOK:
    raise RuntimeError("FEISHU_WEBHOOK not found")

def send(text):
    data = {
        "msg_type": "text",
        "content": {
            "text": text
        }
    }

    req = urllib.request.Request(
        WEBHOOK,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )

    urllib.request.urlopen(req)

if __name__ == "__main__":
    send("✅ GitHub 雪茄监控机器人测试成功")
