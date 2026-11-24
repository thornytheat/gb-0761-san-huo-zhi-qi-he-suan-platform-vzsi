from flask import request

from .config import FILES, ROOT
from .errors import Rejected


def sample(name):
    if not isinstance(name, str) or name not in {"clean", "dirty"}:
        raise Rejected("UNKNOWN_SAMPLE", status=404)
    return {key: (ROOT / "sample_data" / name / f"{key}.csv").read_text(encoding="utf-8") for key in FILES}


def read_sources():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        raise Rejected("JSON_OBJECT_REQUIRED", status=400)
    if set(payload) == {"sample"}:
        return sample(payload["sample"])
    sources = payload.get("sources")
    if set(payload) != {"sources"} or not isinstance(sources, dict) or set(sources) != set(FILES):
        raise Rejected("FOUR_SOURCES_REQUIRED", status=400)
    if any(not isinstance(text, str) or len(text) > 250_000 for text in sources.values()):
        raise Rejected("INVALID_SOURCE_SIZE", status=400)
    return {key: sources[key] for key in FILES}
