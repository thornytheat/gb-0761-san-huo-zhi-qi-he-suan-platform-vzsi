import csv
import io

from app.errors import Rejected
from app.reasons import issue
from .contract import HEADERS
from .values import required


def rows(source, text):
    text = text.removeprefix('\ufeff')
    if not text:
        raise Rejected("EMPTY_FILE", source)
    expected = HEADERS[source].split(',')
    reader = csv.reader(io.StringIO(text, newline=''), strict=True)
    header = None
    stats = {"input": 0, "blank": 0, "headers": 0}
    records, isolated = [], []
    try:
        while True:
            line = reader.line_num + 1
            row = next(reader, None)
            if row is None:
                break
            if not any(value.strip() for value in row):
                if header is not None:
                    stats["input"] += 1
                    stats["blank"] += 1
                continue
            if header is None:
                header = [value.strip() for value in row]
                if sorted(header) != sorted(expected):
                    raise Rejected("BAD_HEADER", source)
                stats["headers"] = 1
                continue
            stats["input"] += 1
            if row == header:
                stats["headers"] += 1
                continue
            if len(row) != len(header):
                isolated.append(issue("COLUMN_COUNT", source, line, row))
                continue
            try:
                fields = {name: required(value) for name, value in zip(header, row)}
                records.append((line, row, fields))
            except ValueError as exc:
                isolated.append(issue(str(exc), source, line, row))
    except csv.Error:
        raise Rejected("CSV_SYNTAX", source) from None
    if header is None:
        raise Rejected("BLANK_FILE", source)
    if not stats["input"] or stats["input"] == stats["blank"] + stats["headers"] - 1:
        if source in {"events", "terms"}:
            raise Rejected("HEADER_ONLY", source)
        stats["state"] = "HEADER_ONLY"
    return records, isolated, stats
