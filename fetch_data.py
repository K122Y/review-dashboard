import akshare as ak
import json
from datetime import datetime

def get_market_data():
    # 1. 拿上证指数（新浪源）
    df = ak.stock_zh_index_spot_sina()
    sh = df[df["代码"] == "sh000001"].iloc[0]

    # 2. 拿全市场涨跌家数（东财源，如果失败会自动降级）
    up_count, down_count, flat_count = 0, 0, 0
    try:
        spot = ak.stock_zh_a_spot_em()
        up_count = int((spot["涨跌幅"] > 0).sum())
        down_count = int((spot["涨跌幅"] < 0).sum())
        flat_count = int((spot["涨跌幅"] == 0).sum())
    except Exception as e:
        print("涨跌家数抓取失败（东财源被限），本次留空：", e)

    data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "sh_close": round(float(sh["最新价"]), 2),
        "sh_change": round(float(sh["涨跌幅"]), 2),
        "sh_amount": int(sh["成交额"]),
        "up_count": up_count,
        "down_count": down_count,
        "flat_count": flat_count,
    }
    return data

if __name__ == "__main__":
    data = get_market_data()
    with open("market_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("数据抓取完成：")
    print(data)