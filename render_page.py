import json
from calc_trend import calc_all_trends

INDEX_TAG = {
    "国证A指": "全市场",
    "沪深300": "大盘蓝筹",
    "中证500": "中盘",
    "中证1000": "小盘",
    "创业板指": "成长型",
    "科创50": "硬科技",
}

def generate_html():
    with open("history.json", "r", encoding="utf-8") as f:
        history = json.load(f)

    dates = sorted(history.keys())
    latest_date = dates[-1]
    latest = history[latest_date]

    trends = calc_all_trends()

    # 全市场成交额
    total_amount = latest.get("total_amount", 0)
    prev_total = 0
    if len(dates) >= 2:
        prev_total = history[dates[-2]].get("total_amount", 0)

    if total_amount > 0 and prev_total > 0:
        pct = round((total_amount - prev_total) / prev_total * 100, 2)
        total_change = f"{'+' if pct > 0 else ''}{pct}%"
        total_change_class = "up" if pct > 0 else ("down" if pct < 0 else "flat")
    else:
        total_change = "—"
        total_change_class = "flat"

    total_yi = total_amount / 1000000000000
    total_text = f"{total_yi:.2f} 万亿" if total_amount > 0 else "—"

    cards_html = ""
    for name, info in latest.items():
        if name in ("total_amount", "update_time"):
            continue
        t = trends.get(name, {})
        change = info.get("change", 0)
        cls = "up" if change > 0 else ("down" if change < 0 else "flat")
        sign = "+" if change > 0 else ""

        amounts = t.get("amounts", [])
        changes = t.get("changes", [])
        bars = ""
        if amounts:
            max_amt = max(amounts) if max(amounts) > 0 else 1
            for i, a in enumerate(amounts):
                h = int(a / max_amt * 28)
                c = changes[i] if i < len(changes) else 0
                color = "#f85149" if c > 0 else ("#3fb950" if c < 0 else "#8b949e")
                bars += f'<div class="bar" style="height:{h}px; background:{color}"></div>'

        amount_yi = info.get("amount", 0) / 100000000
        label = t.get("label", "数据不足")
        label_class = t.get("label_class", "flat")
        ratio = t.get("ratio", 0)
        percentile = t.get("percentile", 0)
        tag = INDEX_TAG.get(name, "")

        cards_html += f'''
        <div class="card">
          <div class="idx-name">{name} <span class="tag">{tag}</span></div>
          <div class="idx-price">{info["close"]:.2f} <span class="{cls}">{sign}{change:.2f}%</span></div>
          <div class="bars">{bars}</div>
          <div class="bottom-line">
            <span>{amount_yi:.2f}亿手</span>
            <span class="label {label_class}">{label}</span>
          </div>
          <div class="bottom-line">
            <span title="今日成交量 ÷ 过去10日平均成交量">量比 {ratio}</span>
            <span title="今日成交量在近10日中的百分位排名">分位 {percentile}%</span>
          </div>
        </div>
        '''

    with open("templates/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    html = html.replace("{{ date }}", latest_date)
    html = html.replace("{{ update_time }}", latest.get("update_time", ""))
    html = html.replace("{{ total_amount }}", total_text)
    html = html.replace("{{ total_change }}", total_change)
    html = html.replace("{{ total_change_class }}", total_change_class)
    html = html.replace("{{ cards }}", cards_html)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("网页已生成：index.html")

if __name__ == "__main__":
    generate_html()