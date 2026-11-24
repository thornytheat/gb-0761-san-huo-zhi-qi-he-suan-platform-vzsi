import hashlib
import json
from datetime import datetime, timezone
from time import perf_counter

from .config import RULE


def snapshot(sources, results, started):
    signatures = {key: hashlib.sha256(value.encode()).hexdigest() for key, value in sources.items()}
    parameters = {"timezone": "UTC", "clock_unit": "minute", "currency": "USD"}
    identity = json.dumps([RULE, signatures, parameters], sort_keys=True)
    return {"run_id": hashlib.sha256(identity.encode()).hexdigest(), "rule": RULE,
            "source_sha256": signatures, "parameters": parameters,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "duration_ms": round((perf_counter() - started) * 1000), "results": results}
