#!/usr/bin/env python3
"""Compare Podcast() parse time : current set_soup vs. from_encoding="utf-8".

Tests the IHRACP-9134 hypothesis : declaring the encoding when constructing
BeautifulSoup skips chardet's encoding detection, which profiling showed costs
~90% of parse time on feeds that lack an <?xml ...?> prolog.

For each feed it reports BEFORE (current code) vs AFTER (from_encoding="utf-8"):
  * median wall time over N runs (PROFILE_RUNS env var, default 3)
  * speedup factor
  * an equivalence check on stable text fields (guid/title/description) so we
    catch any encoding corruption that would break the byte-for-byte criteria

Usage :
    PROFILE_RUNS=3 python scripts/compare_encoding.py [<feed.rss> ...]
"""

import hashlib
import os
import statistics
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bs4 import BeautifulSoup  # noqa : E402
from pypodcastparser.Podcast import Podcast  # noqa : E402
from pypodcastparser.Error import InvalidPodcastFeed  # noqa : E402

RUNS = int(os.environ.get("PROFILE_RUNS", "3"))

# Keep a reference to the unmodified method so we can restore it.
_ORIGINAL_SET_SOUP = Podcast.set_soup


def _set_soup_utf8(self):
    """set_soup variant that declares from_encoding='utf-8' to bypass chardet.

    Mirrors the branching of the real Podcast.set_soup exactly; the only
    difference is the from_encoding kwarg passed to BeautifulSoup.
    """
    if self.feed_content.startswith(b"<?xml"):
        self.soup = BeautifulSoup(
            self.feed_content, features="lxml-xml", from_encoding="utf-8"
        )
    else:
        c = self.feed_content
        try:
            recovered_content = c[c.index(b"<?xml") :]
            self.soup = BeautifulSoup(
                recovered_content, features="lxml-xml", from_encoding="utf-8"
            )
        except Exception:
            self.soup = BeautifulSoup(
                self.feed_content, features="lxml-xml", from_encoding="utf-8"
            )


def time_parse(feed_content, runs):
    """Return wall-clock timings (seconds) for `runs` full Podcast() builds."""
    timings = []
    for _ in range(runs):
        start = time.perf_counter()
        Podcast(feed_content)
        timings.append(time.perf_counter() - start)
    return timings


def content_fingerprint(feed_content):
    """md5 over stable, encoding-sensitive text fields of every item.

    Excludes published_date: its exception path uses datetime.now(), which is
    non-deterministic and would cause false mismatches. guid/title/description
    come straight from tag.string, so they reflect any encoding corruption.
    """
    podcast = Podcast(feed_content)
    h = hashlib.md5()
    h.update(repr(podcast.title).encode("utf-8", "replace"))
    for item in podcast.items:
        h.update(
            repr((item.guid, item.title, item.description)).encode("utf-8", "replace")
        )
    return len(podcast.items), h.hexdigest()


def report(feed_path):
    feed_content = Path(feed_path).read_bytes()
    size_mb = len(feed_content) / 1024 / 1024
    print(f"\n{'=' * 72}")
    print(f"FEED: {Path(feed_path).name}  ({size_mb:.1f} MB)")
    print(f"{'=' * 72}")

    try:
        # BEFORE: current code
        Podcast.set_soup = _ORIGINAL_SET_SOUP
        before_items, before_hash = content_fingerprint(feed_content)
        before = time_parse(feed_content, RUNS)

        # AFTER: from_encoding="utf-8"
        Podcast.set_soup = _set_soup_utf8
        after_items, after_hash = content_fingerprint(feed_content)
        after = time_parse(feed_content, RUNS)
    except InvalidPodcastFeed as e:
        print(f"  [skipped] feed raises InvalidPodcastFeed: {e}")
        return
    finally:
        Podcast.set_soup = _ORIGINAL_SET_SOUP

    before_med = statistics.median(before)
    after_med = statistics.median(after)
    speedup = before_med / after_med if after_med else float("inf")

    print(f"  runs per variant : {RUNS}")
    print(f"  BEFORE (current) : {before_med * 1000:>12.1f} ms median")
    print(f"  AFTER  (utf-8)   : {after_med * 1000:>12.1f} ms median")
    print(
        f"  speedup          : {speedup:>12.2f}x  "
        f"({(1 - after_med / before_med) * 100:.1f}% faster)"
    )
    print(
        f"  items before/after : {before_items} / {after_items}  "
        f"{'OK' if before_items == after_items else '!! MISMATCH'}"
    )
    equiv = (
        "OK -- identical content" if before_hash == after_hash else "!! CONTENT DIFFERS"
    )
    print(f"  content fingerprint: {equiv}")
    if before_hash != after_hash:
        print(f"      before md5={before_hash}")
        print(f"      after  md5={after_hash}")


def main():
    args = sys.argv[1:]
    if args:
        feeds = [Path(a) for a in args]
    else:
        feeds = sorted((REPO_ROOT / "tests" / "Ian_test_feeds").glob("*.rss"))
        print(
            f"Comparing {len(feeds)} feeds in tests/Ian_test_feeds/ "
            f"({RUNS} runs per variant)"
        )

    for feed in feeds:
        if not feed.exists():
            print(f"\n!! skipping missing feed: {feed}")
            continue
        report(feed)


if __name__ == "__main__":
    main()
