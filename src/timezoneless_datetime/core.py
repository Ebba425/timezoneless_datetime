"""Core implementation for timezoneless datetimes."""

from __future__ import annotations

import calendar
import re
from datetime import date, datetime, time, timedelta, tzinfo
from typing import Any, Optional, Union


_ISO_RE = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})"
    r"(?:[T ](?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})"
    r"(?:\.(?P<microsecond>\d{1,6}))?)?$"
)


class NaiveDateTime:
    """A datetime explicitly without timezone information.

    The internal value is always stored as a standard library
    ``datetime`` with ``tzinfo=None``. All operations return new
    ``NaiveDateTime`` instances; the class is immutable.
    """

    __slots__ = ("_dt",)

    def __init__(
        self,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        microsecond: int = 0,
    ) -> None:
        """Create a new timezoneless datetime.

        Args:
            year: 1..9999
            month: 1..12
            day: 1..number of days in the given month and year
            hour: 0..23
            minute: 0..59
            second: 0..59
            microsecond: 0..999999

        Raises:
            ValueError: If any component is out of range.
        """
        self._dt = datetime(
            year, month, day, hour, minute, second, microsecond, tzinfo=None
        )

    @classmethod
    def from_datetime(cls, dt: datetime) -> "NaiveDateTime":
        """Create an instance from a standard library datetime.

        If ``dt`` has a timezone, that information is discarded. This is an
        explicit design decision: the point of this library is to represent
        datetimes *without* timezone information. Use ``as_datetime()`` on the
        result to get a naive standard library datetime back.
        """
        return cls(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            dt.second,
            dt.microsecond,
        )

    @classmethod
    def from_isoformat(cls, value: str) -> "NaiveDateTime":
        """Parse an ISO 8601 datetime without a timezone offset.

        Accepted forms are ``YYYY-MM-DD``, ``YYYY-MM-DDTHH:MM:SS`` and
        ``YYYY-MM-DDTHH:MM:SS.ffffff``. A space may be used instead of ``T``.
        The microsecond part may have 1 to 6 digits; missing digits are
        right-padded with zeros. Anything with a timezone offset, ``Z``
        suffix, or extra components is rejected. This strictness avoids
        silently dropping information that the caller may not have intended
        to discard.
        """
        match = _ISO_RE.match(value.strip())
        if not match:
            raise ValueError(f"Invalid timezoneless ISO datetime: {value!r}")

        parts = match.groupdict()
        microsecond = 0
        if parts["microsecond"] is not None:
            microsecond = int(parts["microsecond"].ljust(6, "0"))

        return cls(
            int(parts["year"]),
            int(parts["month"]),
            int(parts["day"]),
            int(parts["hour"] or 0),
            int(parts["minute"] or 0),
            int(parts["second"] or 0),
            microsecond,
        )

    @classmethod
    def now(cls) -> "NaiveDateTime":
        """Return the current local date and time without timezone info.

        This uses ``datetime.now()`` with no tz argument, so the returned
        value is a naive local time. It is included for convenience, but
        callers should be aware that two calls may differ and that the value
        is only meaningful in the local context.
        """
        return cls.from_datetime(datetime.now())

    @property
    def year(self) -> int:
        return self._dt.year

    @property
    def month(self) -> int:
        return self._dt.month

    @property
    def day(self) -> int:
        return self._dt.day

    @property
    def hour(self) -> int:
        return self._dt.hour

    @property
    def minute(self) -> int:
        return self._dt.minute

    @property
    def second(self) -> int:
        return self._dt.second

    @property
    def microsecond(self) -> int:
        return self._dt.microsecond

    def as_datetime(self) -> datetime:
        """Return the value as a standard library naive datetime."""
        return self._dt.replace(tzinfo=None)

    def replace(
        self,
        *,
        year: Optional[int] = None,
        month: Optional[int] = None,
        day: Optional[int] = None,
        hour: Optional[int] = None,
        minute: Optional[int] = None,
        second: Optional[int] = None,
        microsecond: Optional[int] = None,
    ) -> "NaiveDateTime":
        """Return a new instance with the specified fields replaced.

        Only the fields passed as keyword arguments are changed; all other
        components are copied from the current instance.
        """
        return NaiveDateTime(
            self._dt.year if year is None else year,
            self._dt.month if month is None else month,
            self._dt.day if day is None else day,
            self._dt.hour if hour is None else hour,
            self._dt.minute if minute is None else minute,
            self._dt.second if second is None else second,
            self._dt.microsecond if microsecond is None else microsecond,
        )

    def add(self, *, days: int = 0, seconds: int = 0, microseconds: int = 0) -> "NaiveDateTime":
        """Add a duration expressed in days, seconds, and microseconds.

        The three components are converted to a standard library timedelta and
        added to the internal value. The result is range-checked by the
        datetime constructor, so adding a duration that would push the value
        out of the supported year range raises ValueError.
        """
        try:
            result = self._dt + timedelta(days=days, seconds=seconds, microseconds=microseconds)
        except OverflowError as exc:
            raise ValueError("Resulting datetime out of range") from exc
        return NaiveDateTime.from_datetime(result)

    def subtract(self, *, days: int = 0, seconds: int = 0, microseconds: int = 0) -> "NaiveDateTime":
        """Subtract a duration expressed in days, seconds, and microseconds."""
        return self.add(days=-days, seconds=-seconds, microseconds=-microseconds)

    def diff(self, other: "NaiveDateTime") -> timedelta:
        """Return the timedelta from ``other`` to ``self``."""
        return self._dt - other._dt

    def to_isoformat(self, *, sep: str = "T") -> str:
        """Return an ISO 8601 string without timezone information.

        Args:
            sep: Separator between date and time. Must be ``T`` or a space.

        Returns:
            A string of the form ``YYYY-MM-DDTHH:MM:SS``, or with a fractional
            part if microsecond is nonzero.

        Raises:
            ValueError: If ``sep`` is not ``T`` or ``' '``.
        """
        if sep not in ("T", " "):
            raise ValueError(f"Separator must be 'T' or a space, got {sep!r}")
        base = self._dt.isoformat(sep=sep)
        if self._dt.microsecond == 0:
            base = base[:19]  # strip trailing seconds fraction if zero
        return base

    def weekday(self) -> int:
        """Return the day of the week as an integer, Monday=0..Sunday=6."""
        return self._dt.weekday()

    def is_leap_year(self) -> bool:
        """Return True if the year is a leap year."""
        return calendar.isleap(self._dt.year)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, NaiveDateTime):
            return NotImplemented
        return self._dt == other._dt

    def __lt__(self, other: "NaiveDateTime") -> bool:
        if not isinstance(other, NaiveDateTime):
            return NotImplemented
        return self._dt < other._dt

    def __le__(self, other: "NaiveDateTime") -> bool:
        if not isinstance(other, NaiveDateTime):
            return NotImplemented
        return self._dt <= other._dt

    def __gt__(self, other: "NaiveDateTime") -> bool:
        if not isinstance(other, NaiveDateTime):
            return NotImplemented
        return self._dt > other._dt

    def __ge__(self, other: "NaiveDateTime") -> bool:
        if not isinstance(other, NaiveDateTime):
            return NotImplemented
        return self._dt >= other._dt

    def __hash__(self) -> int:
        return hash(self._dt)

    def __repr__(self) -> str:
        return f"NaiveDateTime({self.to_isoformat()!r})"

    def __str__(self) -> str:
        return self.to_isoformat(sep=" ")
