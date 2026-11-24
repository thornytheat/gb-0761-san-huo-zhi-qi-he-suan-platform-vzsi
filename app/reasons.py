SENTINELS = frozenset({"-", "N/A", "NULL", "未知"})


def issue(code, source, line, raw):
    return {"code": code, "source": source, "line": line, "raw": raw}
