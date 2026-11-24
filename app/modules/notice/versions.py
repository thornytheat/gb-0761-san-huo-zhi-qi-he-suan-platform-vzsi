from app.errors import Rejected


def effective(terms, timestamp):
    candidates = sorted((t for t in terms if t["start"] <= timestamp < t["end"]),
                        key=lambda t: (-t["priority"], t["version"]))
    if not candidates:
        return None, []
    if len(candidates) > 1 and candidates[0]["priority"] == candidates[1]["priority"]:
        raise Rejected("TERM_PRIORITY_TIE", "terms")
    return candidates[0], [term["version"] for term in candidates[1:]]
