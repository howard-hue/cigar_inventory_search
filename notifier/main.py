from pathlib import Path
import glob
from notifier.storage import load_latest, save_latest

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
    print(f"本次商品数：{len(rows)}")
    save_latest(rows)
    print("已更新 latest.json")


if __name__ == "__main__":
    main()
