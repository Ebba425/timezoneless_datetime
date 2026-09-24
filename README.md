# timezoneless-datetime

A small Python library for representing and manipulating datetimes that are explicitly timezone-free.

```python
from timezoneless_datetime import NaiveDateTime

ndt = NaiveDateTime(2024, 6, 15, 8, 30, 45)
print(ndt.to_isoformat())
# 2024-06-15T08:30:45

later = ndt.add(days=1)
print(later.to_isoformat(sep=" "))
# 2024-06-16 08:30:45
```

## Why this exists

Standard library `datetime` objects can be either naive (no timezone) or aware (with a timezone). Code that needs to work with local times often has to check `tzinfo` repeatedly and handle the ambiguity. This library provides a single immutable type that is always naive, so the intent is explicit: the value has no timezone and must not be treated as UTC or as local time. The trade-off is that any timezone information present when converting from a `datetime` is discarded. That is deliberate; if you need to preserve the original offset, keep the original `datetime`.

## Awkward edge

`from_isoformat` rejects strings that include a timezone offset or `Z` suffix. It does so because silently dropping that information would be exactly the kind of mistake this library is meant to prevent. Parse with a timezone-aware method first, convert to the desired local time, and then pass the resulting naive `datetime` to `from_datetime` if that is what you mean.

## API

### `NaiveDateTime(year, month, day, hour=0, minute=0, second=0, microsecond=0)`

Create a new timezoneless datetime.

### Class methods

- `NaiveDateTime.from_datetime(dt)` — create an instance from a standard library `datetime`; any `tzinfo` is discarded.
- `NaiveDateTime.from_isoformat(value)` — parse `YYYY-MM-DD`, `YYYY-MM-DDTHH:MM:SS`, or `YYYY-MM-DDTHH:MM:SS.ffffff`; timezone offsets and `Z` are rejected.
- `NaiveDateTime.now()` — current local naive datetime.

### Properties

`year`, `month`, `day`, `hour`, `minute`, `second`, `microsecond`.

### Methods

- `as_datetime()` — return as a standard library naive `datetime`.
- `replace(*, year=None, month=None, day=None, hour=None, minute=None, second=None, microsecond=None)` — return a new instance with the given fields replaced.
- `add(*, days=0, seconds=0, microseconds=0)` — add a duration.
- `subtract(*, days=0, seconds=0, microseconds=0)` — subtract a duration.
- `diff(other)` — return a `timedelta` from `other` to `self`.
- `to_isoformat(*, sep="T")` — ISO string; `sep` must be `"T"` or `" "`.
- `weekday()` — Monday=0 through Sunday=6.
- `is_leap_year()` — boolean.

Instances support equality, ordering, hashing, `str`, and `repr`.
