from datetime import datetime, timedelta

from app.errors import Rejected
from .versions import effective


def decide(events, terms):
    ready = next((r for r in events if r["kind"] == "READY" and r["party"] == "PORT"), None)
    if ready is None:
        raise Rejected("NO_PORT_READINESS", "events")
    decisions, chosen = [], None
    for row in (r for r in events if r["kind"] == "NOR"):
        item = {"notice": row["event_id"], "line": row["line"], "time": row["time"], "shadowed_terms": []}
        if row["party"] != "SHIP" or row["time"] < ready["time"]:
            item["code"] = "PREMATURE_OR_WRONG_PARTY"
        elif chosen is not None:
            item["code"] = "ALREADY_TENDERED"
        else:
            term, shadowed = effective(terms, row["time"])
            if term:
                chosen = (row, term)
                item.update(code="ACCEPTED_NOR", version=term["version"], shadowed_terms=shadowed)
            else:
                item["code"] = "NO_EFFECTIVE_TERM"
        decisions.append(item)
    if chosen is None:
        raise Rejected("NO_VALID_NOTICE", "events")
    row, term = chosen
    start = (datetime.fromisoformat(row["time"]) + timedelta(minutes=term["wait_min"])).isoformat(timespec="minutes")
    loading = next((r for r in events if r["kind"] == "LOAD_START" and r["party"] == "PORT" and r["time"] >= ready["time"]), None)
    finish = next((r for r in events if r["kind"] == "LOAD_END" and r["party"] == "PORT" and loading and r["time"] >= loading["time"] and r["time"] >= row["time"]), None)
    if finish is None:
        raise Rejected("NO_PORT_COMPLETION", "events")
    if finish["time"] < start:
        raise Rejected("COMPLETED_BEFORE_CLOCK", "events")
    return {"start": start, "end": finish["time"], "term": term, "notice_line": row["line"],
            "readiness_line": ready["line"], "loading_line": loading["line"],
            "completion_line": finish["line"], "decisions": decisions}
