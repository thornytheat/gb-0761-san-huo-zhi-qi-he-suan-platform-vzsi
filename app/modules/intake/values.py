from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from app.reasons import SENTINELS


def required(text):
    value = text.strip()
    if not value:
        raise ValueError("EMPTY_CELL")
    if value in SENTINELS:
        raise ValueError("MISSING_SENTINEL")
    return value


def minute_stamp(text):
    try:
        dt = datetime.fromisoformat(text)
        if dt.tzinfo is None or dt.second or dt.microsecond:
            raise ValueError
        return dt.astimezone(timezone.utc).isoformat(timespec="minutes")
    except (ValueError, OverflowError):
        raise ValueError("INVALID_MINUTE_STAMP") from None


def amount(text, places=2):
    try:
        value = Decimal(text)
        if not value.is_finite() or value < 0 or value > 10**8:
            raise InvalidOperation
        quantized = value.quantize(Decimal(1).scaleb(-places))
        if value != quantized:
            raise InvalidOperation
        return format(abs(quantized), f".{places}f")
    except InvalidOperation:
        raise ValueError("INVALID_AMOUNT") from None
