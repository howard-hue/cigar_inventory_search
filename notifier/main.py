from pathlib import Path
import glob
from notifier.storage import load_latest, save_latest
from notifier.compare import compare
from notifier.csv_reader import load_csv 
from notifier.feishu import send_text

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
    previous = load_latest()
    print(f"上次商品数：{len(previous)}")
    print(f"本次商品数：{len(rows)}")# 第一次运行
    if len(previous) == 0:
        from notifier.feishu import send_text
        send_text("🚀 飞书机器人测试成功！")
        print("第一次运行，不发送通知。")
        save_latest(rows)
        return
    
    changes = compare(previous, rows)

    print(f"新增商品：{len(changes.new)}")
    print(f"下架商品：{len(changes.removed)}")
    print(f"价格变化：{len(changes.price_changed)}")


    ##if changes.new:
    if True:    
        message = f"🎉 检测到 {len(changes.new)} 个新品\n\n"
        for i, item in enumerate(changes.new[:10], start=1):
            message += (
                f"{i}. {item['产品名称']}\n"
                f"🏪 {item['网站']}\n"
                f"💰 ¥{item['人民币税后']}\n"
                f"🔗 {item['链接']}\n\n"
        )

    if len(changes.new) > 10:
        message += f"...还有 {len(changes.new)-10} 个新品"

    send_text(message)

    save_latest(rows)
    send_text("✅ 飞书机器人测试成功")

if __name__ == "__main__":
    main()
