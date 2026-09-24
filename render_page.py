import json

def generate_html():
    # 1. 读取数据
    with open("market_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. 判断涨跌颜色（A股：涨红跌绿）
    change = data["sh_change"]
    if change > 0:
        sh_class = "up"
    elif change < 0:
        sh_class = "down"
    else:
        sh_class = "flat"

    # 3. 格式化成交额：元 -> 亿元，保留 1 位小数
    amount_yi = data["sh_amount"] / 100000000

    # 4. 读取 HTML 模板
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 5. 替换占位符
    html = html.replace("{{ date }}", data["date"])
    html = html.replace("{{ sh_close }}", f"{data['sh_close']:.2f}")
    html = html.replace("{{ sh_change }}", f"{change:.2f}")
    html = html.replace("{{ sh_class }}", sh_class)
    html = html.replace("{{ sh_amount }}", f"{amount_yi:.0f}")
    html = html.replace("{{ up_count }}", str(data["up_count"]))
    html = html.replace("{{ down_count }}", str(data["down_count"]))
    html = html.replace("{{ flat_count }}", str(data["flat_count"]))

    # 6. 输出最终网页
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("网页已生成：index.html")

if __name__ == "__main__":
    generate_html()