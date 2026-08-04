from pathlib import Path
import glob
import json
from notifier.compare import compare
from notifier.csv_reader import load_csv
from notifier.feishu import send_new_products

DATA_DIR = Path("data")
LATEST_FILE = DATA_DIR / "latest.json"


def load_previous() -> list[dict]:
    """从 data/latest.json 读取上次结果"""
    if not LATEST_FILE.exists():
        print(f"[debug] {LATEST_FILE} 不存在，视为首次运行")
        return []
    with LATEST_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"[debug] 从 {LATEST_FILE} 读取到 {len(data)} 条记录")
    return data


def save_latest(rows: list[dict]) -> None:
    """保存本次结果到 data/latest.json"""
    DATA_DIR.mkdir(exist_ok=True)
    with LATEST_FILE.open("w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    print(f"[debug] 已保存 {len(rows)} 条到 {LATEST_FILE}")


def newest_csv() -> Path | None:
    files = glob.glob("inventory_*.csv")
    if not files:
        return None
    files.sort()
    return Path(files[-1])


def main():
    csv_file = newest_csv()
    if csv_file is None:
        print("没有找到 inventory csv")
        return

    rows = load_csv(csv_file)
    print(f"本次商品数：{len(rows)}")

    previous = load_previous()
    print(f"上次商品数：{len(previous)}")

    if len(previous) == 0:
        print("第一次运行，不发送通知。")
        save_latest(rows)
        return

    changes = compare(previous, rows)

    print(f"新增商品：{len(changes.new)}")
    print(f"下架商品：{len(changes.removed)}")
    print(f"价格变化：{len(changes.price_changed)}")

    if changes.new:
        print("开始发送飞书通知...")
        send_new_products(changes.new)
        print("飞书通知发送完成。")

    save_latest(rows)


if __name__ == "__main__":
    main()
