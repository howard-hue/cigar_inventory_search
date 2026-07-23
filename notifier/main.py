from pathlib import Path
import glob
from notifier.storage import load_latest, save_latest
from notifier.compare import compare

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

    from notifier.csv_reader import load_csv 
    rows = load_csv(csv_file)
    previous = load_latest()
    print(f"上次商品数：{len(previous)}")
    print(f"本次商品数：{len(rows)}")# 第一次运行
    if len(previous) == 0:
        print("第一次运行，不发送通知。")
        save_latest(rows)
        return
    changes = compare(previous, rows)
    print(f"新增商品：{len(changes.new)}")
    print(f"下架商品：{len(changes.removed)}")
    print(f"价格变化：{len(changes.price_changed)}")
    save_latest(rows)


if __name__ == "__main__":
    main()
