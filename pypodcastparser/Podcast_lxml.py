# -*- coding: utf-8 -*-
"""SKETCH — lxml-based rewrite of Podcast.py.

Drop-in replacement for `pypodcastparser.Podcast.Podcast`. Same public API
(every attribute, every method name preserved) but parses with
`lxml.etree` directly instead of wrapping every node in a `bs4.element.Tag`.

Compared to Podcast.py:
  * `set_soup` → `_parse` (cached module-level XMLParser with recover=True)
  * `self.soup` → `self.root` (lxml Element)
  * `tag.string` → `bs4_string(tag)`
  * `tag.prefix` / `tag.name` → derived from `tag.tag` via `_qname()`
  * `channel.children` (filtered on Tag) → `channel.iterchildren(tag=etree.Element)`
  * `tag.find("itunes:name", recursive=False)` → `tag.find("itunes:name", namespaces=NS)`
  * `tag.find_all(..., recursive=False)` → `tag.iterchildren(tag=...)`

Item.py needs the matching change — its constructor will take an
`etree.Element` plus the prefix map produced here (see end of file).
"""
from __future__ import annotations

import datetime
import email.utils
from typing import Optional

from lxml import etree

from pypodcastparser.Item_lxml import Item, bs4_string
from pypodcastparser.Error import InvalidPodcastFeed


# Well-known namespace URIs mapped to the short prefixes the dispatch
# tables use. Anything declared in the document's root nsmap overrides
# this at parse time.
_DEFAULT_PREFIXES = {
    "http://www.itunes.com/dtds/podcast-1.0.dtd": "itunes",
    "http://purl.org/rss/1.0/modules/content/": "content",
    "https://podcastindex.org/namespace/1.0": "podcast",
    "http://iheart.com/rss/ihr": "ihr",
}

_ITUNES_NS = "http://www.itunes.com/dtds/podcast-1.0.dtd"
_ITUNES_CATEGORY = f"{{{_ITUNES_NS}}}category"

# One reusable parser. recover=True handles malformed feeds without our
# manual byte-slicing fallback; huge_tree=True lifts libxml2's default
# size limit for very large catalogs.
_PARSER = etree.XMLParser(recover=True, huge_tree=True, resolve_entities=False)


def _qname(tag: str, prefix_map: dict) -> tuple[Optional[str], str]:
    """Convert lxml Clark-notation '{uri}local' (or 'local') to the
    (prefix, name) tuple the dispatch tables key on."""
    if tag and tag[0] == "{":
        uri, _, local = tag[1:].partition("}")
        return prefix_map.get(uri), local
    return None, tag


class Podcast:
    """Parses an XML RSS feed. Same public API as the BS4 version."""

    def __init__(self, feed_content: bytes):
        self.feed_content = feed_content
        self.items: list = []
        self.itunes_categories: list = []
        self.itunes_keywords: list = []

        # Initialize attributes — feed may not populate them
        self.copyright = None
        self.description = None
        self.image_url = None
        self.itunes_author_name = None
        self.itunes_block = False
        self.itunes_complete = None
        self.itunes_explicit = None
        self.itunes_image = None
        self.itunes_new_feed_url = None
        self.language = None
        self.last_build_date = None
        self.link = None
        self.published_date = None
        self.published_date_string = None
        self.summary = None
        self.owner_name = None
        self.owner_email = None
        self.subtitle = None
        self.title = None
        self.date_time = None
        self.itunes_type = None
        self.interactive = False
        self.is_interactive = False

        self.root = self._parse(feed_content)

        # Build the URI→prefix map: defaults overridden by whatever the
        # document itself declares at the root.
        prefix_map = dict(_DEFAULT_PREFIXES)
        for prefix, uri in (self.root.nsmap or {}).items():
            if prefix:
                prefix_map[uri] = prefix
        self._prefix_map = prefix_map

        tag_methods = {
            (None, "copyright"): self.set_copyright,
            (None, "description"): self.set_description,
            (None, "image"): self.set_image,
            (None, "language"): self.set_language,
            (None, "lastBuildDate"): self.set_last_build_date,
            (None, "link"): self.set_link,
            (None, "pubDate"): self.set_published_date,
            (None, "title"): self.set_title,
            (None, "item"): self.add_item,
            ("itunes", "author"): self.set_itunes_author_name,
            ("itunes", "type"): self.set_itunes_type,
            ("itunes", "block"): self.set_itunes_block,
            ("itunes", "category"): self.add_itunes_category,
            ("itunes", "complete"): self.set_itunes_complete,
            ("itunes", "explicit"): self.set_itunes_explicit,
            ("itunes", "image"): self.set_itunes_image,
            ("itunes", "keywords"): self.set_itunes_keywords,
            ("itunes", "new-feed-url"): self.set_itunes_new_feed_url,
            ("itunes", "owner"): self.set_owner,
            ("itunes", "subtitle"): self.set_subtitle,
            ("itunes", "summary"): self.set_summary,
            ("ihr", "interactive"): self.set_interactive,
        }
        many_tag_methods = frozenset(
            {(None, "item"), ("itunes", "category"), ("itunes", "keywords")}
        )

        channel = self.root.find("channel") if self.root is not None else None
        if channel is None:
            raise InvalidPodcastFeed("Invalid Podcast Feed")

        # Walk channel children once — lxml's iterchildren(tag=Element)
        # skips text/comment nodes natively, so no isinstance check needed.
        for c in channel.iterchildren(tag=etree.Element):
            key = _qname(c.tag, prefix_map)
            method = tag_methods.get(key)
            if method is None:
                continue
            # For single-value tags, drop the dispatch entry so a duplicate
            # on an invalid feed gets ignored — matches BS4 .pop() behavior.
            if key not in many_tag_methods:
                tag_methods.pop(key, None)
            method(c)

        if not self.items:
            # Fallback for malformed feeds: walk the whole document for <item>.
            for elem in self.root.iter():
                if _qname(elem.tag, prefix_map) == (None, "item"):
                    self.add_item(elem)

        self.set_time_published()
        self.set_dates_published()

    @staticmethod
    def _parse(feed_content: bytes):
        """Replacement for set_soup(). Tolerates junk before <?xml."""
        try:
            if feed_content and not feed_content.startswith(b"<?xml"):
                idx = feed_content.find(b"<?xml")
                if idx > 0:
                    feed_content = feed_content[idx:]
            root = etree.fromstring(feed_content, parser=_PARSER)
            if root is None:
                raise InvalidPodcastFeed("Invalid Podcast Feed: empty document")
            return root
        except etree.XMLSyntaxError as e:
            raise InvalidPodcastFeed(f"Invalid Podcast Feed: {e}")

    # ------------------------------------------------------------------
    # Setters — same semantics as Podcast.py, with tag.string → bs4_string(tag).
    # Bodies that are pure 1-line `self.X = tag.string` are collapsed.
    # ------------------------------------------------------------------

    def add_item(self, tag):
        self.items.append(Item(tag, self._prefix_map))

    def set_copyright(self, tag): self.copyright = bs4_string(tag)
    def set_description(self, tag): self.description = bs4_string(tag)
    def set_language(self, tag): self.language = bs4_string(tag)
    def set_last_build_date(self, tag): self.last_build_date = bs4_string(tag)
    def set_link(self, tag): self.link = bs4_string(tag)
    def set_title(self, tag): self.title = bs4_string(tag)
    def set_subtitle(self, tag): self.subtitle = bs4_string(tag)
    def set_summary(self, tag): self.summary = bs4_string(tag)
    def set_itunes_author_name(self, tag): self.itunes_author_name = bs4_string(tag)
    def set_itunes_new_feed_url(self, tag): self.itunes_new_feed_url = bs4_string(tag)

    def set_image(self, tag):
        # <image><url>...</url></image> — direct child only.
        try:
            url_elem = tag.find("url")
            self.image_url = bs4_string(url_elem) if url_elem is not None else None
        except Exception:
            raise InvalidPodcastFeed("Invalid Podcast Feed, show level image could not be parsed")

    def set_itunes_type(self, tag):
        text = bs4_string(tag)
        self.itunes_type = text.lower() if text else None

    def set_itunes_block(self, tag):
        # Old behavior: True iff text.lower() == "yes". Other text → False.
        text = (bs4_string(tag) or "").lower()
        self.itunes_block = (text == "yes")

    def set_itunes_complete(self, tag):
        text = bs4_string(tag)
        self.itunes_complete = text.lower() if text else None

    def set_itunes_explicit(self, tag):
        text = bs4_string(tag)
        self.itunes_explicit = text.lower() if text else None

    def set_itunes_image(self, tag):
        self.itunes_image = tag.get("href")

    def set_itunes_keywords(self, tag):
        text = bs4_string(tag)
        if not text:
            self.itunes_keywords = []
            return
        normalized = [" ".join(k.split()) for k in text.split(",")]
        unique = list({k for k in normalized if k})
        self.itunes_keywords = unique

    def set_owner(self, tag):
        ns = {"itunes": _ITUNES_NS}
        name_elem = tag.find("itunes:name", namespaces=ns)
        email_elem = tag.find("itunes:email", namespaces=ns)
        self.owner_name = bs4_string(name_elem) if name_elem is not None else None
        self.owner_email = bs4_string(email_elem) if email_elem is not None else None

    def add_itunes_category(self, tag):
        category_text = tag.get("text")
        if category_text not in self.itunes_categories:
            self.itunes_categories.append(category_text)
        # Recurse into nested <itunes:category> children only.
        for child in tag.iterchildren(tag=_ITUNES_CATEGORY):
            self.add_itunes_category(child)

    def set_published_date(self, tag):
        """Same logic as Podcast.py.set_published_date — only tag.string → bs4_string(tag)."""
        try:
            text = bs4_string(tag)
            self.published_date = text
            self.published_date_string = text
            final_time = text.split(":")
            min_sec = final_time[2]
            seconds = min_sec[:2]
            final_time[0] += ":" + final_time[1]
            final_time[0] += ":" + seconds
            self.published_date = str(
                datetime.datetime.strptime(final_time[0], "%a, %d %b %Y %H:%M:%S")
            )
        except AttributeError:
            self.published_date = None
        except Exception:
            raise InvalidPodcastFeed(
                f"Invalid Podcast Feed, show level pubDate: {bs4_string(tag)}, could not be parsed"
            )

    def set_interactive(self, tag):
        text = bs4_string(tag)
        self.interactive = (text or "").lower() == "yes"
        self.is_interactive = self.interactive

    # ------------------------------------------------------------------
    # Unchanged from Podcast.py — included for completeness.
    # ------------------------------------------------------------------

    def set_time_published(self):
        if self.published_date_string is None:
            self.time_published = None
            return
        try:
            time_tuple = email.utils.parsedate_tz(self.published_date_string)
            self.time_published = email.utils.mktime_tz(time_tuple)
        except (TypeError, ValueError, IndexError):
            self.time_published = None
        except Exception:
            raise InvalidPodcastFeed("Invalid Podcast Feed, show level pubDate could not be parsed")

    def set_dates_published(self):
        if self.time_published is None:
            self.date_time = None
            return
        try:
            self.date_time = datetime.date.fromtimestamp(self.time_published)
        except ValueError:
            self.date_time = None
        except Exception:
            raise InvalidPodcastFeed("Invalid Podcast Feed, show level pubDate could not be parsed")

    def to_dict(self):
        podcast_dict = {
            "copyright": self.copyright,
            "description": self.description,
            "image_url": self.image_url,
            "items": [item.to_dict() for item in self.items],
            "itunes_author_name": self.itunes_author_name,
            "itunes_block": self.itunes_block,
            "itunes_categories": self.itunes_categories,
            "itunes_explicit": self.itunes_explicit,
            "itunes_image": self.itunes_image,
            "itunes_keywords": self.itunes_keywords,
            "itunes_new_feed_url": self.itunes_new_feed_url,
            "language": self.language,
            "last_build_date": self.last_build_date,
            "link": self.link,
            "published_date": self.published_date,
            "owner_name": self.owner_name,
            "owner_email": self.owner_email,
            "subtitle": self.subtitle,
            "title": self.title,
            "itunes_type": self.itunes_type,
        }
        return podcast_dict


