#!/usr/bin/env python3
"""Profile pyPodcastParser feed parsing.

Supports the IHRACP-8704 / PPP-002 spike: confirm whether the secondary
``find_all("item")`` fallback in ``Podcast.__init__`` actually executes on a
given feed, and measure where parsing time goes.

Usage:
    python scripts/profile_parsing.py <feed.rss> [<feed2.rss> ...]
    python scripts/profile_parsing.py            # defaults to tests/test_feeds/*

For each feed it reports:
  * whether the find_all("item") fallback fired (the thing PPP-002 removes)
  * item count
  * median / min / max wall time over N runs
  * a cProfile breakdown of the hottest calls

Run this against `master` first to capture the "before" numbers, then against
the single-pass branch for "after". Same machine, same feed, same N.
"""

import cProfile
import io
import pstats
import statistics
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import bs4  # noqa: E402
from pypodcastparser.Podcast import Podcast  # noqa: E402
from pypodcastparser.Error import InvalidPodcastFeed  # noqa: E402

import os  # noqa: E402

RUNS = int(os.environ.get("PROFILE_RUNS", "50"))  # set PROFILE_RUNS=5 for big feeds


def detect_fallback(feed_content):
    """Parse once with find_all instrumented; report if the fallback fired.

    The secondary pass in Podcast.__init__ is the only place that calls
    BeautifulSoup.find_all during construction, so counting calls tells us
    directly whether PPP-002's target code path is exercised by this feed.
    """
    original_find_all = bs4.BeautifulSoup.find_all
    calls = []

    def counting_find_all(self, *args, **kwargs):
        calls.append((args, kwargs))
        return original_find_all(self, *args, **kwargs)

    bs4.BeautifulSoup.find_all = counting_find_all
    try:
        podcast = Podcast(feed_content)
    finally:
        bs4.BeautifulSoup.find_all = original_find_all

    fallback_fired = any(args and args[0] == "item" for args, _ in calls)
    return fallback_fired, len(podcast.items)


def time_runs(feed_content, runs=RUNS):
    """Return wall-clock timings (seconds) for `runs` full Podcast() builds."""
    timings = []
    for _ in range(runs):
        start = time.perf_counter()
        Podcast(feed_content)
        timings.append(time.perf_counter() - start)
    return timings


def profile_once(feed_content, top=15):
    """Return a cProfile breakdown string for a single Podcast() build."""
    profiler = cProfile.Profile()
    profiler.enable()
    Podcast(feed_content)
    profiler.disable()

    buf = io.StringIO()
    stats = pstats.Stats(profiler, stream=buf).sort_stats("cumulative")
    stats.print_stats(top)
    return buf.getvalue()


def report(feed_path):
    feed_content = Path(feed_path).read_bytes()
    size_kb = len(feed_content) / 1024

    print(f"\n{'=' * 70}")
    print(f"FEED: {feed_path}  ({size_kb:.1f} KB)")
    print(f"{'=' * 70}")

    try:
        fallback_fired, item_count = detect_fallback(feed_content)
        timings = time_runs(feed_content)
    except InvalidPodcastFeed as e:
        # Intentionally malformed fixtures (e.g. invalid_show_dates.rss) raise
        # this from the parser itself. Skip; they're not benchmark candidates.
        print(f"  [skipped] feed raises InvalidPodcastFeed: {e}")
        return

    print(f"  items                           : {item_count}")
    flag = "YES -- PPP-002 target path is exercised" if fallback_fired else "no"
    print(f"  find_all('item') fallback fired : {flag}")
    print(f"  runs                            : {len(timings)}")
    print(
        f"  median                          : {statistics.median(timings) * 1000:.3f} ms"
    )
    print(
        f"  min / max                       : "
        f"{min(timings) * 1000:.3f} / {max(timings) * 1000:.3f} ms"
    )
    print(
        f"  mean                            : {statistics.mean(timings) * 1000:.3f} ms"
    )
    print()
    print("  cProfile (cumulative, top 15):")
    for line in profile_once(feed_content).splitlines():
        print(f"    {line}")


def main():
    args = sys.argv[1:]
    if args:
        feeds = [Path(a) for a in args]
    else:
        feeds = sorted((REPO_ROOT / "tests" / "Ian_test_feeds").glob("*.rss"))
        print(
            f"No feed given; profiling {len(feeds)} test feeds in tests/Ian_test_feeds/"
        )

    for feed in feeds:
        if not feed.exists():
            print(f"\n!! skipping missing feed: {feed}")
            continue
        report(feed)


if __name__ == "__main__":
    main()
