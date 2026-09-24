"""Timezoneless datetime library.

Exposes a single public class, NaiveDateTime, for representing and
manipulating datetimes that are explicitly timezone-free.
"""

from .core import NaiveDateTime

__all__ = ["NaiveDateTime"]
