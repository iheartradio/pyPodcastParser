# -*- coding: utf-8 -*-
"""Correctness tests for Podcast_dateutil's date handling.

Each case states `(pub_date_input, expected_show_date, expected_item_date)`
and verifies the dateutil-based parser produces those exact strings.

Reminder on the contract:
- Show-level (`Podcast.published_date`): drops the timezone, returns
  naive local wall-clock as "YYYY-MM-DD HH:MM:SS".
- Item-level (`Item.published_date`): normalizes to US/Eastern and
  returns naive wall-clock as "YYYY-MM-DD HH:MM:SS".
"""
import datetime
from unittest import mock

import pytest

from pypodcastparser.Podcast import Podcast


# (pub_date_input, expected_show, expected_item)
#
# Item-level expected values account for US/Eastern DST:
#   - 2008-03-{21,24}: EDT (UTC-4)
#   - 2022-05-30:      EDT (UTC-4)
#   - 2023-05-22:      EDT (UTC-4)
#   - 2023-07-06:      EDT (UTC-4)
#   - 2023-12-22:      EST (UTC-5)
DATE_CASES = [
    # (input, show, item)
    ("Mon, 24 Mar 2008 23:30:07 GMT",   "2008-03-24 23:30:07", "2008-03-24 19:30:07"),
    ("Fri, 21 Mar 2008 09:51:00 EDT",   "2008-03-21 09:51:00", "2008-03-21 09:51:00"),
    ("Mon, 30 May 2022 04:05:03 GMT",   "2022-05-30 04:05:03", "2022-05-30 00:05:03"),
    ("Mon, 30 May 2022 04:05:03 PST",   "2022-05-30 04:05:03", "2022-05-30 07:05:03"),
    ("Mon, 30 May 2022 04:05:03 UTC",   "2022-05-30 04:05:03", "2022-05-30 00:05:03"),
    ("Mon, 30 May 2022 04:05:03 EST",   "2022-05-30 04:05:03", "2022-05-30 04:05:03"),
    ("Mon, 30 May 2022 04:05:03 CST",   "2022-05-30 04:05:03", "2022-05-30 05:05:03"),
    ("Mon, 30 May 2022 04:05:03 CDT",   "2022-05-30 04:05:03", "2022-05-30 05:05:03"),
    ("Mon, 30 May 2022 04:05:03 MST",   "2022-05-30 04:05:03", "2022-05-30 06:05:03"),
    ("Mon, 30 May 2022 04:05:03 MDT",   "2022-05-30 04:05:03", "2022-05-30 06:05:03"),
    ("Mon, 22 May 2023 14:00:00 +1000", "2023-05-22 14:00:00", "2023-05-22 00:00:00"),
    ("Thu, 06 Jul 2023 01:00:00 PDT",   "2023-07-06 01:00:00", "2023-07-06 04:00:00"),
    ("Mon, 22 Dec 2023 14:00:00 -0800", "2023-12-22 14:00:00", "2023-12-22 17:00:00"),
    ("Mon, 22 Dec 2023 14:00:00 +1200", "2023-12-22 14:00:00", "2023-12-21 21:00:00"),
]


_VALID_SHOW_DATE = "Mon, 01 Jan 2024 12:00:00 GMT"


def _make_feed(pub_date: str, show_date: str = None) -> bytes:
    """Minimal RSS doc. `pub_date` goes on the item; `show_date` (default:
    a known-good value) goes at the channel level so item-only tests
    don't accidentally trip the show-level parse."""
    show = show_date if show_date is not None else pub_date
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0">'
        '<channel>'
        '<title>date-test</title>'
        '<description>date-test</description>'
        f'<pubDate>{show}</pubDate>'
        '<item>'
        '<title>ep</title>'
        '<guid>ep-1</guid>'
        f'<pubDate>{pub_date}</pubDate>'
        '</item>'
        '</channel>'
        '</rss>'
    ).encode("utf-8")


@pytest.mark.parametrize(
    "pub_date,expected_show,expected_item",
    DATE_CASES,
    ids=[c[0] for c in DATE_CASES],
)
def test_show_published_date(pub_date, expected_show, expected_item):
    podcast = Podcast(_make_feed(pub_date))
    assert podcast.published_date == expected_show, (
        f"show-level wrong for {pub_date!r}: "
        f"got {podcast.published_date!r}, expected {expected_show!r}"
    )


@pytest.mark.parametrize(
    "pub_date,expected_show,expected_item",
    DATE_CASES,
    ids=[c[0] for c in DATE_CASES],
)
def test_item_published_date(pub_date, expected_show, expected_item):
    podcast = Podcast(_make_feed(pub_date))
    item_date = podcast.items[0].published_date
    assert item_date == expected_item, (
        f"item-level wrong for {pub_date!r}: "
        f"got {item_date!r}, expected {expected_item!r}"
    )


@pytest.mark.parametrize(
    "pub_date,expected_show,expected_item",
    DATE_CASES,
    ids=[c[0] for c in DATE_CASES],
)
def test_item_date_time_is_a_date(pub_date, expected_show, expected_item):
    """`item.date_time` is derived from email.utils.parsedate_tz +
    datetime.date.fromtimestamp, which uses the machine's local timezone.
    Asserting a specific calendar date here would be flaky across CI
    machines, so just confirm the type wires through correctly."""
    podcast = Podcast(_make_feed(pub_date))
    assert isinstance(podcast.items[0].date_time, datetime.date)


def test_missing_pubdate_leaves_none():
    """No <pubDate> at either level → published_date stays at the
    initial None value because the setter is never dispatched."""
    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0">'
        '<channel>'
        '<title>no-date</title>'
        '<description>no-date</description>'
        '<item>'
        '<title>ep</title>'
        '<guid>ep-1</guid>'
        '</item>'
        '</channel>'
        '</rss>'
    ).encode("utf-8")
    podcast = Podcast(feed)
    assert podcast.published_date is None
    assert podcast.items[0].published_date is None


def test_malformed_item_pubdate_falls_back_to_now():
    """Item-level: unparseable pubDate → current US/Eastern time string
    (legacy contract). Show-level pubDate is valid so the parse reaches
    the item dispatch.

    `datetime.now` is frozen so the fallback is deterministic. Comparing a
    parse-time timestamp against a fresh `now()` at assert time is a
    wall-clock race that flakes on cold CI runs (first run is ~5x slower
    from imports/bytecode compilation).
    """
    from pypodcastparser import Item as item_module

    frozen = datetime.datetime(2024, 6, 15, 9, 30, 0, tzinfo=item_module._US_EASTERN)
    feed = _make_feed("nonsense-not-a-date", show_date=_VALID_SHOW_DATE)

    with mock.patch("pypodcastparser.Item.datetime") as mock_datetime:
        mock_datetime.datetime.now.return_value = frozen
        mock_datetime.date = datetime.date  # keep real date for other code paths
        podcast = Podcast(feed)
        item_date = podcast.items[0].published_date

    assert item_date == "2024-06-15 09:30:00"


def test_malformed_show_pubdate_raises():
    """Show-level: unparseable pubDate → InvalidPodcastFeed with the
    raw text echoed in the message."""
    from pypodcastparser.Error import InvalidPodcastFeed
    feed = _make_feed(_VALID_SHOW_DATE, show_date="nonsense-not-a-date")
    with pytest.raises(InvalidPodcastFeed) as exc_info:
        Podcast(feed)
    assert "nonsense-not-a-date" in str(exc_info.value)
