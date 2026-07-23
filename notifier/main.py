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

    print(f"读取: {csv_file}")


if __name__ == "__main__":
    main()
