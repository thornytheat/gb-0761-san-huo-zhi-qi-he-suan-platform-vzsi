from datetime import datetime, timedelta

from .minutes import minutes


def replay(notice, segments):
    limit = notice["term"]["allow_min"]
    totals = {"counted": 0, "exempt": 0, "missing": 0}
    rows, crossed = [], None
    for segment in segments:
        duration = minutes(segment["start"], segment["end"])
        bucket = segment["bucket"]
        allowance = min(duration, max(0, limit - totals["counted"])) if bucket == "counted" else 0
        overtime = duration - allowance if bucket == "counted" else 0
        totals[bucket] += duration
        if overtime and crossed is None:
            time = datetime.fromisoformat(segment["start"]) + timedelta(minutes=allowance)
            crossed = time.isoformat(timespec="minutes")
        rows.append({**segment, "minutes": duration, "allowance_min": allowance, "overtime_min": overtime,
                     "cumulative_counted_min": totals["counted"]})
    elapsed = minutes(notice["start"], notice["end"])
    return {"elapsed_min": elapsed, **totals, "allowance_min": limit,
            "overtime_min": max(0, totals["counted"] - limit), "overtime_start": crossed,
            "balanced": elapsed == sum(totals.values()), "rows": rows}
