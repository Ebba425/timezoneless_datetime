"""Tests for timezoneless datetime core."""

import unittest
from datetime import datetime, timedelta

from timezoneless_datetime import NaiveDateTime


class TestConstruction(unittest.TestCase):
    def test_basic_construction(self):
        ndt = NaiveDateTime(2024, 2, 29, 12, 30, 45, 123456)
        self.assertEqual(ndt.year, 2024)
        self.assertEqual(ndt.month, 2)
        self.assertEqual(ndt.day, 29)
        self.assertEqual(ndt.hour, 12)
        self.assertEqual(ndt.minute, 30)
        self.assertEqual(ndt.second, 45)
        self.assertEqual(ndt.microsecond, 123456)

    def test_defaults_are_zero(self):
        ndt = NaiveDateTime(2024, 1, 1)
        self.assertEqual(ndt.hour, 0)
        self.assertEqual(ndt.minute, 0)
        self.assertEqual(ndt.second, 0)
        self.assertEqual(ndt.microsecond, 0)

    def test_invalid_date_raises(self):
        with self.assertRaises(ValueError):
            NaiveDateTime(2023, 2, 29)

    def test_invalid_time_component_raises(self):
        with self.assertRaises(ValueError):
            NaiveDateTime(2024, 1, 1, hour=24)


class TestFromDatetime(unittest.TestCase):
    def test_naive_datetime_roundtrip(self):
        dt = datetime(2024, 6, 15, 8, 30, 0, 42)
        ndt = NaiveDateTime.from_datetime(dt)
        self.assertEqual(ndt.as_datetime(), dt)

    def test_aware_datetime_discards_tz(self):
        tz = datetime.now().astimezone().tzinfo
        aware = datetime(2024, 6, 15, 8, 30, tzinfo=tz)
        ndt = NaiveDateTime.from_datetime(aware)
        self.assertIsNone(ndt.as_datetime().tzinfo)
        self.assertEqual(
            (ndt.year, ndt.month, ndt.day, ndt.hour, ndt.minute, ndt.second),
            (2024, 6, 15, 8, 30, 0),
        )


class TestISOFormat(unittest.TestCase):
    def test_parse_date_only(self):
        ndt = NaiveDateTime.from_isoformat("2024-06-15")
        self.assertEqual(ndt.as_datetime(), datetime(2024, 6, 15))

    def test_parse_full_with_t(self):
        ndt = NaiveDateTime.from_isoformat("2024-06-15T08:30:45")
        self.assertEqual(ndt.as_datetime(), datetime(2024, 6, 15, 8, 30, 45))

    def test_parse_full_with_space(self):
        ndt = NaiveDateTime.from_isoformat("2024-06-15 08:30:45")
        self.assertEqual(ndt.as_datetime(), datetime(2024, 6, 15, 8, 30, 45))

    def test_parse_with_microseconds(self):
        ndt = NaiveDateTime.from_isoformat("2024-06-15T08:30:45.123456")
        self.assertEqual(ndt.microsecond, 123456)

    def test_parse_short_microseconds_pads_right(self):
        ndt = NaiveDateTime.from_isoformat("2024-06-15T08:30:45.1")
        self.assertEqual(ndt.microsecond, 100000)

    def test_parse_rejects_timezone_offset(self):
        with self.assertRaises(ValueError):
            NaiveDateTime.from_isoformat("2024-06-15T08:30:45+02:00")

    def test_parse_rejects_z_suffix(self):
        with self.assertRaises(ValueError):
            NaiveDateTime.from_isoformat("2024-06-15T08:30:45Z")

    def test_to_isoformat_zero_microsecond(self):
        ndt = NaiveDateTime(2024, 6, 15, 8, 30, 45)
        self.assertEqual(ndt.to_isoformat(), "2024-06-15T08:30:45")

    def test_to_isoformat_with_microsecond(self):
        ndt = NaiveDateTime(2024, 6, 15, 8, 30, 45, 42)
        self.assertEqual(ndt.to_isoformat(), "2024-06-15T08:30:45.000042")

    def test_to_isoformat_space_separator(self):
        ndt = NaiveDateTime(2024, 6, 15, 8, 30, 45)
        self.assertEqual(ndt.to_isoformat(sep=" "), "2024-06-15 08:30:45")

    def test_to_isoformat_invalid_separator(self):
        ndt = NaiveDateTime(2024, 6, 15)
        with self.assertRaises(ValueError):
            ndt.to_isoformat(sep="_")


class TestArithmetic(unittest.TestCase):
    def test_add_days(self):
        ndt = NaiveDateTime(2024, 1, 31)
        result = ndt.add(days=1)
        self.assertEqual(result.as_datetime(), datetime(2024, 2, 1))

    def test_add_seconds_carries(self):
        ndt = NaiveDateTime(2024, 1, 1, 23, 59, 59)
        result = ndt.add(seconds=1)
        self.assertEqual(result.as_datetime(), datetime(2024, 1, 2, 0, 0, 0))

    def test_subtract_days(self):
        ndt = NaiveDateTime(2024, 3, 1)
        result = ndt.subtract(days=1)
        self.assertEqual(result.as_datetime(), datetime(2024, 2, 29))

    def test_diff_positive(self):
        a = NaiveDateTime(2024, 6, 15, 12, 0, 0)
        b = NaiveDateTime(2024, 6, 15, 10, 0, 0)
        self.assertEqual(a.diff(b), timedelta(hours=2))

    def test_diff_negative(self):
        a = NaiveDateTime(2024, 6, 15, 10, 0, 0)
        b = NaiveDateTime(2024, 6, 15, 12, 0, 0)
        self.assertEqual(a.diff(b), timedelta(hours=-2))

    def test_add_out_of_range_raises(self):
        ndt = NaiveDateTime(9999, 12, 31, 23, 59, 59)
        with self.assertRaises(ValueError):
            ndt.add(seconds=1)


class TestComparisonAndProperties(unittest.TestCase):
    def test_equality(self):
        a = NaiveDateTime(2024, 6, 15, 8, 30)
        b = NaiveDateTime(2024, 6, 15, 8, 30)
        self.assertEqual(a, b)

    def test_inequality(self):
        a = NaiveDateTime(2024, 6, 15, 8, 30)
        b = NaiveDateTime(2024, 6, 15, 8, 31)
        self.assertNotEqual(a, b)

    def test_ordering(self):
        a = NaiveDateTime(2024, 6, 15, 8, 30)
        b = NaiveDateTime(2024, 6, 16, 8, 30)
        self.assertLess(a, b)
        self.assertLessEqual(a, b)
        self.assertGreater(b, a)
        self.assertGreaterEqual(b, a)

    def test_hashable(self):
        ndt = NaiveDateTime(2024, 6, 15)
        self.assertEqual(hash(ndt), hash(NaiveDateTime(2024, 6, 15)))

    def test_weekday(self):
        # 2024-06-15 is a Saturday
        ndt = NaiveDateTime(2024, 6, 15)
        self.assertEqual(ndt.weekday(), 5)

    def test_is_leap_year(self):
        self.assertTrue(NaiveDateTime(2024, 1, 1).is_leap_year())
        self.assertFalse(NaiveDateTime(2023, 1, 1).is_leap_year())

    def test_replace(self):
        ndt = NaiveDateTime(2024, 6, 15, 8, 30)
        replaced = ndt.replace(month=7, hour=9)
        self.assertEqual(replaced.as_datetime(), datetime(2024, 7, 15, 9, 30))

    def test_str_and_repr(self):
        ndt = NaiveDateTime(2024, 6, 15, 8, 30, 45)
        self.assertEqual(str(ndt), "2024-06-15 08:30:45")
        self.assertIn("NaiveDateTime", repr(ndt))


if __name__ == "__main__":
    unittest.main()
