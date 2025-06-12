from decimal import Decimal
from datetime import date, time, datetime, timedelta, timezone

def _parse_time_millis(ms: int) -> time:
    # ms since midnight → a time object
    return (datetime.min + timedelta(milliseconds=ms)).time()

def _parse_time_micros(us: int) -> time:
    # µs since midnight → a time object
    return (datetime.min + timedelta(microseconds=us)).time()

def _parse_local_timestamp_millis(ms: int) -> datetime:
    # ms since epoch → naive local datetime (no TZ)
    return datetime.utcfromtimestamp(ms / 1000)

def _parse_local_timestamp_micros(us: int) -> datetime:
    # µs since epoch → naive local datetime (no TZ)
    return datetime.utcfromtimestamp(us / 1_000_000)

def _parse_timestamp_millis(ms: int) -> datetime:
    # ms since epoch → aware UTC datetime
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)

def _parse_timestamp_micros(us: int) -> datetime:
    # µs since epoch → aware UTC datetime
    return datetime.fromtimestamp(us / 1_000_000, tz=timezone.utc)


LOGICAL_TYPE_MAP = {
    # logicalType: (typename, import-module, parser_func)
    "date": (
        "date",
        "datetime",
        date.fromisoformat,       # expects "YYYY-MM-DD"
    ),
    "time-millis": (
        "time",
        "datetime",
        _parse_time_millis,
    ),
    "time-micros": (
        "time",
        "datetime",
        _parse_time_micros,
    ),
    "timestamp-millis": (
        "datetime",
        "datetime",
        _parse_timestamp_millis,
    ),
    "timestamp-micros": (
        "datetime",
        "datetime",
        _parse_timestamp_micros,
    ),
    "local-timestamp-millis": (
        "datetime",
        "datetime",
        _parse_local_timestamp_millis,
    ),
    "local-timestamp-micros": (
        "datetime",
        "datetime",
        _parse_local_timestamp_micros,
    ),
    "decimal": (
        "Decimal",
        "decimal",
        Decimal,                  # simply wraps the raw bytes/str → Decimal
    ),
}
