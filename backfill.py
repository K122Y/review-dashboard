import akshare as ak
import json

INDEX_MAP = {
    "sz399317": "国证A指",
    "sh000300": "沪深300",
    "sh000905": "中证500",
    "sh000852": "中证1000",
    "sz399006": "创业板指",
    "sh000688": "科创50",
}

def backfill(days=20):
    per_index = {}
    for code, name in INDEX_MAP.items():
        print(f"正在拉取 {name}（{code}）...")
        try:
            df = ak.stock_zh_index_daily(symbol=code)
            df["date"] = df["date"].astype(str)
            df = df.sort_values("date").tail(days).reset_index(drop=True)
            per_index[name] = df
        except Exception as e:
            print(f"  {name} 拉取失败：{e}")

    # 取所有指数日期的交集
    date_sets = [set(df["date"]) for df in per_index.values()]
    common_dates = set.intersection(*date_sets) if date_sets else set()
    common_dates = sorted(common_dates)[-days:]

    history = {}
    for d in common_dates:
        history[d] = {}
        for name, df in per_index.items():
            row = df[df["date"] == d]
            if len(row) == 0:
                continue
            idx = row.index[0]
            r = row.iloc[0]

            # 算涨跌幅：用前一天的收盘价
            change = 0
            if idx > 0:
                prev_close = float(df.iloc[idx - 1]["close"])
                cur_close = float(r["close"])
                if prev_close:
                    change = round((cur_close - prev_close) / prev_close * 100, 2)

            amount = 0
            for col in ["amount", "volume"]:
                if col in r.index and r[col] == r[col]:
                    amount = float(r[col])
                    break

            history[d][name] = {
                "close": round(float(r["close"]), 2),
                "change": change,
                "amount": amount,
            }

    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

    print(f"\n补历史完成，共 {len(history)} 个交易日")
    print("日期范围：", list(history.keys())[:1], "~", list(history.keys())[-1:])

if __name__ == "__main__":
    backfill(days=20)