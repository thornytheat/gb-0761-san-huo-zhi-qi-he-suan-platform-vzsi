STOP_RULES = {"GAP": (30, "missing"), "HOLIDAY": (20, "exempt"), "RAIN": (10, "exempt")}


def adjudicate(active):
    ordered = sorted(active, key=lambda stop: (-STOP_RULES[stop["kind"]][0], stop["stop_id"]))
    if not ordered:
        return {"bucket": "counted", "reason": "WORKING_CLOCK", "winner": None, "sources": []}
    winner = ordered[0]
    return {"bucket": STOP_RULES[winner["kind"]][1], "reason": winner["kind"],
            "winner": winner["stop_id"],
            "sources": [{"id": row["stop_id"], "kind": row["kind"], "line": row["line"],
                         "start": row["start"], "end": row["end"]} for row in ordered]}
