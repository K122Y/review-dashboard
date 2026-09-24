import json

def calc_all_trends():
    with open("history.json", "r", encoding="utf-8") as f:
        history = json.load(f)

    dates = sorted(history.keys())
    if len(dates) < 2:
        return {}

    latest_date = dates[-1]
    latest = history[latest_date]

    trends = {}
    for name in latest.keys():
        if name in ("total_amount", "update_time"):
            continue
        amounts = []
        changes = []
        for d in dates[-10:]:
            if name in history[d] and isinstance(history[d][name], dict):
                amounts.append(history[d][name]["amount"])
                changes.append(history[d][name]["change"])

        if len(amounts) < 2:
            trends[name] = {"label": "数据不足", "label_class": "flat",
                            "ratio": 0, "percentile": 0, "amounts": amounts,
                            "changes": changes}
            continue

        today_amount = amounts[-1]
        avg_amount = sum(amounts) / len(amounts)
        ratio = round(today_amount / avg_amount, 2) if avg_amount > 0 else 0

        sorted_amts = sorted(amounts)
        rank = sorted_amts.index(today_amount) if today_amount in sorted_amts else 0
        percentile = round(rank / (len(sorted_amts) - 1) * 100) if len(sorted_amts) > 1 else 0

        label, label_class = judge_label(amounts, changes)

        trends[name] = {
            "label": label,
            "label_class": label_class,
            "ratio": ratio,
            "percentile": percentile,
            "amounts": amounts,
            "changes": changes,
        }
    return trends

def judge_label(amounts, changes):
    if len(amounts) < 3:
        return "数据不足", "flat"
    a1, a2, a3 = amounts[-3], amounts[-2], amounts[-1]
    c3 = changes[-1] if len(changes) >= 1 else 0

    rising = a1 < a2 < a3
    falling = a1 > a2 > a3
    stable = max(a1, a2, a3) / min(a1, a2, a3) < 1.1 if min(a1, a2, a3) > 0 else False

    if rising and c3 > 0:
        return "量价齐升", "up-strong"
    if rising and c3 < 0:
        return "放量下跌", "down-strong"
    if falling and c3 > 0:
        return "缩量上涨", "warn"
    if falling and c3 < 0:
        return "量价齐跌", "down-strong"
    if stable:
        return "量能平稳", "flat"
    if rising:
        return "连续放量", "up"
    if falling:
        return "连续缩量", "down"
    return "量能平稳", "flat"

if __name__ == "__main__":
    result = calc_all_trends()
    print(json.dumps(result, ensure_ascii=False, indent=2))