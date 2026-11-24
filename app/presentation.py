NAMES = {"intake": "装卸事件采信", "notice": "准备通知裁决", "exceptions": "例外区间切片", "clock": "免计边界复算",
         "ledger": "滞期费与账单", "runs": "批次留档复跑", "evidence": "证据包签发"}


def panel(stage, result):
    if stage == "intake":
        return ("原件核收", ("来源", "输入行", "采信行", "隔离行", "分段"),
                [(key, row["input"], row["accepted"], row["isolated"], row["headers"]) for key, row in result["statistics"].items()])
    if stage == "notice":
        return ("通知采信记录", ("通知", "原行", "UTC", "裁决", "版本", "被覆盖版本"),
                [(r["notice"], r["line"], r["time"], r["code"], r.get("version"), ', '.join(r["shadowed_terms"])) for r in result["decisions"]])
    if stage == "exceptions":
        return ("停工交叠记录", ("起点 UTC", "终点 UTC", "裁决", "胜出", "原始依据"),
                [(r["start"], r["end"], r["reason"], r["winner"], ' / '.join(f'{s["id"]} #{s["line"]}' for s in r["sources"])) for r in result["segments"]])
    return ("计时分段记录", ("起点 UTC", "终点 UTC", "裁决", "分钟", "用额分钟", "超额分钟"),
            [(r["start"], r["end"], r["reason"], r["minutes"], r["allowance_min"], r["overtime_min"]) for r in result["rows"]])
