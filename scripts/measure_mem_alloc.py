"""Run pypodcastparser memory measurement N times per feed; report median peak.

Fetches each feed once, then parses N times with each implementation
(Podcast vs Podcast_lxml), capturing tracemalloc peak per run.
"""

import gc
import statistics
import sys
import tracemalloc
from time import perf_counter

from podcasts.rss import _get_feed_content, clean_content_encoded
from pypodcastparser.Error import InvalidPodcastFeed
from pypodcastparser.Podcast import Podcast
from pypodcastparser.Podcast_lxml import Podcast as Podcast_lxml


FEEDS = [
    "https://feeds.redcircle.com/b5a293e2-0ba9-44f0-8744-4ab98a7928f2",
    "https://anchor.fm/s/1d5aebec/podcast/rss",
    "https://rss.libsyn.com/shows/560300/destinations/4840795.xml",
    "https://www.omnycontent.com/d/playlist/e73c998e-6e60-432f-8610-ae210140c5b1/b0033a5f-8d6c-46a0-90bd-afb90153a86d/b71608e3-ebff-402a-8ca1-afb90153a898/podcast.rss",
    "https://chainsawhorror.com/feed/mp3/",
    "https://feed.podbean.com/thedjsessions/feed.xml",
]

N_RUNS = 5


def fetch(rss_url: str) -> bytes:
    response = _get_feed_content(rss_url)
    response.raise_for_status()
    return clean_content_encoded(response.content)


def measure_peak(parser_cls, cleaned_xml: bytes) -> tuple[int, int, float]:
    gc.collect()
    tracemalloc.start()
    start = perf_counter()
    try:
        podcast = parser_cls(cleaned_xml)
    except InvalidPodcastFeed as exc:
        tracemalloc.stop()
        raise RuntimeError(f"InvalidPodcastFeed: {exc}") from exc
    elapsed = perf_counter() - start
    _, peak = tracemalloc.get_traced_memory()
    n_items = len(podcast.items)
    tracemalloc.stop()
    del podcast
    gc.collect()
    return peak, n_items, elapsed


def run_feed(rss_url: str) -> None:
    print(f"\n=== feed: {rss_url}")
    cleaned_xml = fetch(rss_url)
    print(f"feed bytes: {len(cleaned_xml):,}")

    rows = []
    for label, cls in (("Podcast (bs4)", Podcast), ("Podcast_lxml", Podcast_lxml)):
        peaks = []
        times = []
        n_items = 0
        for _ in range(N_RUNS):
            peak, n_items, elapsed = measure_peak(cls, cleaned_xml)
            peaks.append(peak)
            times.append(elapsed)
        median_kb = statistics.median(peaks) / 1024
        min_kb = min(peaks) / 1024
        max_kb = max(peaks) / 1024
        median_ms = statistics.median(times) * 1000
        min_ms = min(times) * 1000
        max_ms = max(times) * 1000
        rows.append((label, n_items, median_kb, min_kb, max_kb, median_ms, min_ms, max_ms))

    print(f"items:      {rows[0][1]:,}")
    print(f"runs:       {N_RUNS}")
    print()
    print(
        f"  {'impl':<16}  {'med KB':>10}  {'min KB':>10}  {'max KB':>10}  "
        f"{'KB/item':>9}  {'med ms':>9}  {'min ms':>9}  {'max ms':>9}  {'ms/item':>9}"
    )
    for label, n_items, med_kb, mn_kb, mx_kb, med_ms, mn_ms, mx_ms in rows:
        kb_per_item = med_kb / n_items if n_items else 0
        ms_per_item = med_ms / n_items if n_items else 0
        print(
            f"  {label:<16}  {med_kb:>10,.1f}  {mn_kb:>10,.1f}  {mx_kb:>10,.1f}  "
            f"{kb_per_item:>9,.2f}  {med_ms:>9,.1f}  {mn_ms:>9,.1f}  {mx_ms:>9,.1f}  {ms_per_item:>9,.3f}"
        )
    # Ratios
    orig_kb, lxml_kb = rows[0][2], rows[1][2]
    orig_ms, lxml_ms = rows[0][5], rows[1][5]
    print()
    if lxml_kb:
        print(f"  memory reduction:  {(1 - lxml_kb / orig_kb) * 100:.1f}%  ({orig_kb / lxml_kb:.2f}x less)")
    if lxml_ms:
        print(f"  time speedup:      {(1 - lxml_ms / orig_ms) * 100:.1f}%  ({orig_ms / lxml_ms:.2f}x faster)")


if __name__ == "__main__":
    for feed in FEEDS:
        try:
            run_feed(feed)
        except Exception as exc:
            print(f"\n!! feed failed: {feed}\n   {type(exc).__name__}: {exc}")
