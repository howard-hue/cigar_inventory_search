from pathlib import Path
import glob

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
    print(f"读取 {len(rows)} 条商品")


if __name__ == "__main__":
    main()
