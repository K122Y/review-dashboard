import akshare as ak
import json
from datetime import datetime

INDEX_MAP = {
    "sz399317": "国证A指",
    "sh000300": "沪深300",
    "sh000905": "中证500",
    "sh000852": "中证1000",
    "sz399006": "创业板指",
    "sh000688": "科创50",
}

def get_total_amount():
    try:
        spot = ak.stock_zh_a_spot()
        total = int(spot["成交额"].sum())
        print(f"全市场成交额（新浪源）：{total}")
        return total
    except Exception as e:
        print("新浪源全市场成交额抓取失败：", e)
        return 0

def get_market_data():
    indices = {}
    real_date = None
    for code, name in INDEX_MAP.items():
        try:
            df = ak.stock_zh_index_daily(symbol=code)
            df = df.sort_values("date")
            r = df.iloc[-1]
            prev = df.iloc[-2] if len(df) >= 2 else r

            if real_date is None:
                real_date = str(r["date"])

            close = float(r["close"])
            prev_close = float(prev["close"])
            change = round((close - prev_close) / prev_close * 100, 2) if prev_close else 0
            amount = 0
            for col in ["amount", "volume"]:
                if col in r.index and r[col] == r[col]:
                    amount = float(r[col])
                    break
            indices[name] = {
                "close": round(close, 2),
                "change": change,
                "amount": amount,
            }
        except Exception as e:
            print(f"{name} 抓取失败：{e}")
            indices[name] = {"close": 0, "change": 0, "amount": 0}

    data = {
        "date": real_date if real_date else datetime.now().strftime("%Y-%m-%d"),
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "indices": indices,
        "total_amount": get_total_amount(),
    }
    return data

def append_history(data):
    try:
        with open("history.json", "r", encoding="utf-8") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = {}

    date_str = data["date"]
    history[date_str] = {
        "total_amount": data.get("total_amount", 0),
        "update_time": data.get("update_time", ""),
    }
    for name, info in data["indices"].items():
        history[date_str][name] = {
            "close": info["close"],
            "change": info["change"],
            "amount": info["amount"],
        }

    keys = sorted(history.keys())[-30:]
    history = {k: history[k] for k in keys}

    with open("history.json", "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    data = get_market_data()
    append_history(data)
    print("数据抓取完成：")
    print(json.dumps(data, ensure_ascii=False, indent=2))