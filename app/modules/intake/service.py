from collections import Counter, defaultdict
from datetime import datetime

from app.config import FILES
from app.reasons import issue
from .reader import rows
from .values import amount, minute_stamp


def normalize(source, value):
    value = dict(value)
    for key in {"time", "start", "end"} & value.keys():
        value[key] = minute_stamp(value[key])
    if "start" in value and value["start"] >= value["end"]:
        raise ValueError("REVERSED_RANGE")
    if source == "events":
        if value["kind"] not in {"READY", "NOR", "LOAD_START", "LOAD_END"} or value["party"] not in {"PORT", "SHIP"}:
            raise ValueError("UNKNOWN_EVENT")
    if source == "stops" and value["kind"] not in {"RAIN", "HOLIDAY", "GAP"}:
        raise ValueError("UNKNOWN_STOP")
    for key in value:
        if key.endswith('_min') or key in {"minutes", "priority", "tier", "usd"}:
            places = 2 if key.startswith("rate") or key == "usd" else 0
            numeric = amount(value[key], places)
            value[key] = numeric if places else int(numeric)
    if source == "invoice" and value["tier"] not in {1, 2}:
        raise ValueError("UNKNOWN_TIER")
    return value


def accept(sources):
    accepted, statistics, isolated = {}, {}, []
    keys = {"events": "event_id", "stops": "stop_id", "terms": "version", "invoice": "tier"}
    for source in FILES:
        records, issues, stats = rows(source, sources[source])
        groups = defaultdict(list)
        for line, raw, fields in records:
            try:
                value = normalize(source, fields)
                groups[value[keys[source]]].append((line, raw, value))
            except ValueError as exc:
                issues.append(issue(str(exc), source, line, raw))
        output = []
        for group in groups.values():
            first, *repeats = group
            if any(row[2] != first[2] for row in repeats):
                issues.extend({**issue("KEY_CONFLICT", source, line, raw), "key": value[keys[source]]}
                              for line, raw, value in group)
                continue
            output.append({**first[2], "line": first[0], "raw": first[1]})
            issues.extend(issue("EXACT_DUPLICATE", source, line, raw) for line, raw, _ in repeats)
        if source == "events":
            output.sort(key=lambda row: (datetime.fromisoformat(row["time"]), row["event_id"]))
        stats.update(accepted=len(output), isolated=len(issues))
        stats["balanced"] = stats["input"] == stats["headers"] - 1 + stats["blank"] + len(output) + len(issues)
        statistics[source] = stats
        accepted[source] = output
        isolated.extend(sorted(issues, key=lambda row: row["line"]))
    return {"accepted": accepted, "statistics": statistics, "isolated": isolated,
            "reason_counts": dict(Counter(row["code"] for row in isolated))}
