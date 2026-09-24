import akshare as ak

# 拿上证指数实时行情（新浪源）
df = ak.stock_zh_index_spot_sina()
print(df.head(10))
print("\n列名：", df.columns.tolist())