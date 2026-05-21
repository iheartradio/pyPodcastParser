#!/usr/bin/env python3
"""One-off diagnostics for IHRACP-9134: explain the test4 and test5 anomalies.

test5: prove the current parse path mis-decodes valid UTF-8 (mojibake), by
       showing what encoding bs4 actually lands on and the resulting text.
test4: profile what consumes the ~34s that REMAINS after the chardet bypass,
       so we know whether the encoding fix is the whole story for it.
"""

import cProfile
import io
import pstats
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from bs4 import BeautifulSoup  # noqa: E402
from pypodcastparser.Podcast import Podcast  # noqa: E402

FEEDS = REPO_ROOT / "tests" / "Ian_test_feeds"


def diagnose_test5():
    print("=" * 72)
    print("test5.rss  --  encoding mis-detection (slow AND wrong)")
    print("=" * 72)
    b = (FEEDS / "test5.rss").read_bytes()

    t = time.perf_counter()
    soup_current = BeautifulSoup(b, features="lxml-xml")  # current set_soup path
    print(f"  current path : bs4 decoded as {soup_current.original_encoding!r}"
          f"   ({time.perf_counter() - t:.1f}s)")

    t = time.perf_counter()
    soup_utf8 = BeautifulSoup(b, features="lxml-xml", from_encoding="utf-8")
    print(f"  utf-8 path   : bs4 decoded as {soup_utf8.original_encoding!r}"
          f"   ({time.perf_counter() - t:.1f}s)")

    for name in ("copyright", "title", "description"):
        cur = soup_current.find(name)
        utf = soup_utf8.find(name)
        cur_s = cur.string if cur else None
        utf_s = utf.string if utf else None
        verdict = "SAME" if cur_s == utf_s else ">>> DIFFERENT (current = mojibake)"
        print(f"\n  <{name}>")
        print(f"    current : {cur_s!r}")
        print(f"    utf-8   : {utf_s!r}")
        print(f"    {verdict}")


def diagnose_test4():
    print("\n")
    print("=" * 72)
    print("test4.rss  --  where the ~34s AFTER the chardet bypass goes")
    print("=" * 72)
    b = (FEEDS / "test4.rss").read_bytes()

    # Parse with chardet bypassed, so the profile shows only the residual cost.
    original = Podcast.set_soup

    def set_soup_utf8(self):
        self.soup = BeautifulSoup(
            self.feed_content, features="lxml-xml", from_encoding="utf-8"
        )

    Podcast.set_soup = set_soup_utf8
    try:
        pr = cProfile.Profile()
        pr.enable()
        podcast = Podcast(b)
        pr.disable()
    finally:
        Podcast.set_soup = original

    print(f"  items parsed: {len(podcast.items)}")
    for idx, item in enumerate(podcast.items):
        for attr in ("title", "description", "content_encoded", "itunes_summary"):
            value = getattr(item, attr, None)
            size = len(value) if value else 0
            print(f"  item[{idx}].{attr:16s}: {size:,} chars")

    for sort_key in ("tottime", "cumulative"):
        buf = io.StringIO()
        pstats.Stats(pr, stream=buf).sort_stats(sort_key).print_stats(15)
        print(f"\n  --- cProfile sorted by {sort_key} (top 15) ---")
        for line in buf.getvalue().splitlines():
            print(f"  {line}")


if __name__ == "__main__":
    diagnose_test5()
    diagnose_test4()
