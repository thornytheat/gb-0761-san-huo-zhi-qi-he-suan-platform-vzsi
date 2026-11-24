from collections import defaultdict

from .precedence import adjudicate


def slice_window(notice, stops):
    start, end = notice["start"], notice["end"]
    starts, ends = defaultdict(list), defaultdict(list)
    outside = []
    for stop in stops:
        left, right = max(start, stop["start"]), min(end, stop["end"])
        if left >= right:
            outside.append({"id": stop["stop_id"], "line": stop["line"], "code": "OUTSIDE_CLOCK"})
            continue
        starts[left].append(stop)
        ends[right].append(stop["stop_id"])
    points = sorted({start, end, *starts, *ends})
    active = {}
    segments = []
    for left, right in zip(points, points[1:]):
        for stop_id in ends[left]:
            del active[stop_id]
        for stop in starts[left]:
            active[stop["stop_id"]] = stop
        segments.append({"start": left, "end": right, **adjudicate(active.values())})
    return {"segments": segments, "outside": outside,
            "overlaps": sum(len(seg["sources"]) > 1 for seg in segments)}
