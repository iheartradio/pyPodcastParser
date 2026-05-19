# -*- coding: utf-8 -*-
"""SKETCH — lxml-based rewrite of Item.py.

Drop-in replacement for `pypodcastparser.Item.Item`. Same public API and
attributes as the BS4 version; constructor now takes an lxml.etree.Element
plus the prefix_map produced by Podcast_lxml.
"""
from __future__ import annotations

import datetime
from datetime import timezone
import email.utils
import logging
import re
from typing import Optional

import pytz

from lxml import etree

from pypodcastparser.Error import InvalidPodcastFeed


LOGGER = logging.getLogger(__name__)


pytz_timezone_set = set(pytz.all_timezones)  # set instead of list (O(1) lookups)

common_timezones = {
    "IDLW": "Pacific/Midway",
    "NUT": "Pacific/Niue",
    "MART": "Pacific/Marquesas",
    "AKST": "America/Anchorage",
    "MST": "America/Denver",
    "EST": "America/New_York",
    "VET": "America/Caracas",
    "BRT": "America/Sao_Paulo",
    "GST": "Asia/Dubai",
    "AZOT": "Atlantic/Azores",
    "MSK": "Europe/Moscow",
    "PKT": "Asia/Karachi",
    "NPT": "Asia/Kathmandu",
    "MMT": "Asia/Rangoon",
    "ICT": "Asia/Bangkok",
    "AWST": "Australia/Perth",
    "ACWST": "Australia/Eucla",
    "GMT": "GMT",
    "ACST": "Australia/Adelaide",
    "AEDT": "Australia/Sydney",
    "CHAST": "Pacific/Chatham",
    "NZDT": "Pacific/Auckland",
    "LINT": "Pacific/Kiritimati",
    "UTC": "UTC",
    "CET": "Europe/Berlin",
    "EET": "Africa/Cairo",
    "EAT": "Africa/Addis_Ababa",
    "IST": "Asia/Kolkata",
    "BST": "Europe/London",
    "JST": "Asia/Tokyo",
    "ACT": "Australia/ACT",
    "SST": "Pacific/Pago_Pago",
    "NST": "America/St_Johns",
    "HST": "America/Adak",
    "AST": "America/Puerto_Rico",
    "PST": "US/Pacific",
    "CST": "US/Central",
    "CAT": "Africa/Maputo",
    "AEST": "Australia/Sydney",
    "PDT": "America/Los_Angeles",
    "NZST": "Pacific/Auckland",
}

# Map of timezone offsets to timezone abbreviations
offset_map = {
    "-1200": "IDLW", "-1100": "NUT", "-1000": "HST", "-0930": "MART",
    "-0900": "AKST", "-0800": "PST", "-0700": "MST", "-0600": "CST",
    "-0500": "EST", "-0430": "VET", "-0400": "AST", "-0330": "NST",
    "-0300": "BRT", "-0200": "GST", "-0100": "AZOT", "-0000": "GMT",
    "+0000": "GMT", "+0100": "CET", "+0200": "EET", "+0300": "MSK",
    "+0400": "GST", "+0500": "PKT", "+0545": "NPT", "+0600": "BST",
    "+0630": "MMT", "+0700": "ICT", "+0800": "AWST", "+0845": "ACWST",
    "+0900": "JST", "+0930": "ACST", "+1000": "AEST", "+1030": "ACST",
    "+1100": "AEDT", "+1200": "NZST", "+1245": "CHAST", "+1300": "NZDT",
    "+1400": "LINT",
}

# Precompile the regexes used by set_published_date — was uncompiled in BS4
# version, ran 5×per-episode-per-feed.
_DATE_PATTERNS = [
    re.compile(p) for p in (
        r"^[a-zA-Z]{3},$",
        r"^\d{1,2}$",
        r"^[a-zA-Z]{3}$",
        r"^\d{4}$",
        r"^\d\d:\d\d",
    )
]
_TZ_ABBREV_RE = re.compile(r"^[a-zA-Z]{3}$")


_PODCAST_NS = "https://podcastindex.org/namespace/1.0"


def _qname(tag: str, prefix_map: dict) -> tuple[Optional[str], str]:
    """Convert lxml Clark-notation '{uri}local' (or 'local') to the
    (prefix, name) tuple the dispatch tables key on."""
    if tag and tag[0] == "{":
        uri, _, local = tag[1:].partition("}")
        return prefix_map.get(uri), local
    return None, tag


def bs4_string(elem) -> Optional[str]:
    """Emulate BeautifulSoup's `tag.string` semantics on an lxml element.

    BS4's `.string` returns:
      * `None` if the tag has zero or multiple children (mixed content)
      * the text of the single text child, OR
      * the recursive `.string` of the single tag child (single-chain to text)

    This matters for RSS feeds where descriptions contain wrapped HTML like
    `<description><p>text</p></description>` — BS4 returns "text" while
    lxml's `.text` returns `None`.
    """
    if elem is None:
        return None
    n = len(elem)
    if n == 0:
        return elem.text
    if n == 1 and not elem.text:
        child = elem[0]
        if not child.tail:
            return bs4_string(child)
    return None


class Item:
    """Parses one RSS <item>. Same public API as the BS4 Item."""

    def __init__(self, elem, prefix_map: dict):
        self.elem = elem
        self._prefix_map = prefix_map

        # Initialize attributes — feeds may not populate them
        self.author = None
        self.description = None
        self.enclosure_url = None
        self.enclosure_type = None
        self.enclosure_length = None
        self.content_encoded = None
        self.guid = None
        self.itunes_author_name = None
        self.itunes_episode_type = None
        self.itunes_block = False
        self.itunes_duration = None
        self.itunes_season = None
        self.itunes_episode = None
        self.itunes_explicit = None
        self.itunes_image = None
        self.itunes_order = None
        self.itunes_subtitle = None
        self.itunes_summary = None
        self.published_date = None
        self.published_date_string = None
        self.title = None
        self.date_time = None
        self.interactive = None
        self.is_interactive = None
        self.podcast_transcript = None
        self.transcriptionList = []
        self.alternate_enclosures = []

        tag_methods = {
            (None, "title"): self.set_title,
            (None, "author"): self.set_author,
            (None, "description"): self.set_description,
            (None, "guid"): self.set_guid,
            (None, "pubDate"): self.set_published_date,
            (None, "enclosure"): self.set_enclosure,
            # Preserved from BS4 version (dead-code: not callable, but
            # never hit in real feeds — mirrors the original behavior).
            (None, "is_interactive"): self.is_interactive,
            ("content", "encoded"): self.set_content_encoded,
            ("itunes", "author"): self.set_itunes_author_name,
            ("itunes", "episode"): self.set_itunes_episode,
            ("itunes", "episodeType"): self.set_itunes_episode_type,
            ("itunes", "block"): self.set_itunes_block,
            ("itunes", "season"): self.set_itunes_season,
            ("itunes", "duration"): self.set_itunes_duration,
            ("itunes", "explicit"): self.set_itunes_explicit,
            ("itunes", "image"): self.set_itunes_image,
            ("podcast", "transcript"): self.set_podcast_transcript,
            ("itunes", "order"): self.set_itunes_order,
            ("itunes", "subtitle"): self.set_itunes_subtitle,
            ("itunes", "summary"): self.set_itunes_summary,
            ("ihr", "interactive"): self.set_interactive,
            ("podcast", "alternateEnclosure"): self.set_alternate_enclosure,
        }

        for c in elem.iterchildren(tag=etree.Element):
            key = _qname(c.tag, prefix_map)
            if key[1] in ("transcript", "alternateEnclosure"):
                # Multiple-occurrence tags: look up without removing.
                method = tag_methods.get(key)
            else:
                # Single-value tag: pop on first hit to skip duplicates
                # on invalid feeds (matches BS4 .pop() behavior).
                method = tag_methods.pop(key, None)
            if method is None:
                continue
            method(c)

        self.set_time_published()
        self.set_dates_published()

    # ------------------------------------------------------------------
    # Identical to BS4 Item — included for completeness.
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
            raise InvalidPodcastFeed(
                f"Invalid Podcast Feed, episode level pubDate: {self.published_date_string}, could not be parsed"
            )

    def set_dates_published(self):
        if self.time_published is None:
            self.date_time = None
            return
        try:
            self.date_time = datetime.date.fromtimestamp(self.time_published)
        except ValueError:
            self.date_time = None
        except Exception:
            raise InvalidPodcastFeed(
                f"Invalid Podcast Feed, episode level pubDate: {self.published_date_string}, could not be parsed"
            )

    def to_dict(self):
        return {
            "external_id": self.guid,
            "episode_duration": self.itunes_duration,
            "is_explicit": self.itunes_explicit,
            "episode_number": self.itunes_episode,
            "episode_season": self.itunes_season,
            "episode_type": self.itunes_episode_type,
            "external_image_url": self.itunes_image,
            "episode_subtitle": self.itunes_subtitle,
            "episode_description": self.description,
            "original_air_date": self.published_date,
            "start_date": self.published_date,
            "episode_title": self.title,
            "interactive": self.interactive,
            "external_url": self.enclosure_url,
            "enclosure_type": self.enclosure_type,
            "enclosure_length": self.enclosure_length,
            "transcription": self.podcast_transcript,
            "alternate_enclosures": self.alternate_enclosures,
        }

    # ------------------------------------------------------------------
    # Setters — tag.string → bs4_string(tag). Behavior preserved exactly.
    # ------------------------------------------------------------------

    def set_rss_element(self):
        """Set each of the basic rss elements."""
        self.set_enclosure()

    def set_author(self, tag):
        try:
            self.author = bs4_string(tag)
        except AttributeError:
            self.author = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level author could not be parsed"
            )

    def set_description(self, tag):
        try:
            self.description = bs4_string(tag)
        except AttributeError:
            self.description = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level description could not be parsed"
            )

    def set_content_encoded(self, tag):
        try:
            self.content_encoded = bs4_string(tag)
            if self.description is None:
                self.description = self.content_encoded
        except AttributeError:
            self.content_encoded = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level content_encoded could not be parsed"
            )

    def set_enclosure(self, tag):
        try:
            self.enclosure_url = tag.get("url")
            if self.enclosure_url is None:
                # BS4 tag["url"] raises KeyError → caught → set to None.
                # lxml .get returns None — keep as-is for parity.
                pass
        except Exception:
            self.enclosure_url = None
        try:
            self.enclosure_type = tag.get("type")
        except Exception:
            self.enclosure_type = None
        try:
            self.enclosure_length = tag.get("length")
            if self.enclosure_length is not None:
                self.enclosure_length = int(self.enclosure_length)
        except Exception:
            self.enclosure_length = None

    def set_guid(self, tag):
        try:
            self.guid = bs4_string(tag)
        except AttributeError:
            self.guid = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level guid could not be parsed"
            )

    def set_published_date(self, tag):
        """Same algorithm as Item.set_published_date — tag.string → bs4_string(tag),
        regexes precompiled."""
        try:
            text = bs4_string(tag)
            self.published_date = text
            self.published_date_string = text

            if text is None:
                raise AttributeError

            deconstructed_date = text.split(" ")
            if len(deconstructed_date) < 4:
                raise AttributeError

            published_date_timezone = ""
            # Check for timezone abbreviation
            if _TZ_ABBREV_RE.match(deconstructed_date[-1]):
                published_date_timezone = deconstructed_date[-1]
                deconstructed_date.pop()
            else:
                # Check for specific timezone offsets
                for offset, tz in offset_map.items():
                    if offset in self.published_date:
                        published_date_timezone = tz
                        deconstructed_date.pop()
                        break
            if not published_date_timezone:
                published_date_timezone = "EST"

            new_array = []
            for array_index, pattern in enumerate(_DATE_PATTERNS):
                # The original code's outer `re.match(deconstructed_date[i], array_value)`
                # is preserved verbatim — note that calling re.match on a
                # *string-as-pattern* almost never matches in practice, so this
                # branch effectively always falls through to the inner loop.
                if array_index < len(deconstructed_date) and re.match(
                    deconstructed_date[array_index], pattern.pattern
                ):
                    new_array.append(pattern.pattern)
                else:
                    for inner_value in deconstructed_date:
                        if pattern.match(inner_value):
                            new_array.append(inner_value)
                            break

            if len(new_array) != 5:
                raise AttributeError(
                    "Error creating new date array. Array is not of length 5 for formatting"
                )

            date_string = " ".join(new_array)

            time = date_string.split(":")
            if len(time) == 2:
                minutes = time[1].split(" ")
                minutes[0] += ":00"
                time[0] += ":" + minutes[0]
                self.published_date = datetime.datetime.strptime(
                    time[0], "%a, %d %b %Y %H:%M:%S"
                )
            elif len(time) == 3:
                time[0] += ":" + time[1]
                seconds = time[2]
                seconds_string = seconds[:2]
                time[0] += ":" + seconds_string
                self.published_date = datetime.datetime.strptime(
                    time[0], "%a, %d %b %Y %H:%M:%S"
                )
            else:
                # Preserved verbatim from BS4 version (this branch is broken
                # in the original — strptime on a datetime raises — so it
                # always falls through to the outer except).
                now = datetime.datetime.now(timezone.utc)
                published_date_timezone = "UTC"
                self.published_date = datetime.datetime.strptime(
                    now, "%a, %d %b %Y %H:%M:%S"
                )

            if published_date_timezone not in ("ET", "EST", "EDT"):
                if published_date_timezone in pytz_timezone_set:
                    current_timezone = pytz.timezone(published_date_timezone)
                else:
                    current_timezone = pytz.timezone(
                        common_timezones.get(published_date_timezone)
                    )

                date_in_current_timezone = current_timezone.localize(
                    self.published_date
                )
                self.published_date = str(
                    date_in_current_timezone.astimezone(
                        pytz.timezone("US/Eastern")
                    ).replace(tzinfo=None)
                )
                LOGGER.info("Final Published Date EST: %s", self.published_date)
            else:
                LOGGER.info("Final Published Date EST: %s", self.published_date)

        except Exception:
            self.published_date = datetime.datetime.now(
                pytz.timezone("US/Eastern")
            ).strftime("%Y-%m-%d %H:%M:%S")

    def set_title(self, tag):
        try:
            self.title = bs4_string(tag)
        except AttributeError:
            self.title = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level title could not be parsed"
            )

    def set_itunes_author_name(self, tag):
        try:
            self.itunes_author_name = bs4_string(tag)
        except AttributeError:
            self.itunes_author_name = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level itunes:author could not be parsed"
            )

    def set_itunes_episode(self, tag):
        try:
            self.itunes_episode = bs4_string(tag)
            if self.itunes_episode == "" or self.itunes_episode is None:
                self.itunes_episode = "0"
        except AttributeError:
            self.itunes_episode = "0"
        except Exception:
            raise InvalidPodcastFeed(
                f"Invalid Podcast Feed, episode level itunes:episode: {bs4_string(tag)}, could not be parsed"
            )

    def set_podcast_transcript(self, tag):
        """Multiple transcripts allowed — append to list."""
        try:
            transcript_dict = {
                "url": tag.get("url"),
                "type": tag.get("type"),
                "language": tag.get("language"),
                "rel": tag.get("rel"),
            }
            self.transcriptionList.append(transcript_dict)
            self.podcast_transcript = self.transcriptionList
        except AttributeError:
            self.podcast_transcript = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode transcription could not be parsed"
            )

    def set_itunes_season(self, tag):
        try:
            self.itunes_season = bs4_string(tag)
            if self.itunes_season == "" or self.itunes_season is None:
                self.itunes_season = "0"
        except AttributeError:
            self.itunes_season = "0"

    def set_itunes_episode_type(self, tag):
        try:
            text = bs4_string(tag)
            self.itunes_episode_type = text.lower() if text else None
        except AttributeError:
            self.itunes_episode_type = None
        except Exception:
            raise InvalidPodcastFeed(
                f"Invalid Podcast Feed, episode level itunes:episodeType: {bs4_string(tag)}, could not be parsed"
            )

    def set_itunes_block(self, tag):
        try:
            text = bs4_string(tag)
            block = text.lower() if text else ""
        except AttributeError:
            block = ""
        except Exception:
            raise InvalidPodcastFeed(
                f"Invalid Podcast Feed, episode level itunes:block: {bs4_string(tag)}, could not be parsed"
            )
        self.itunes_block = (block == "yes")

    def set_itunes_duration(self, tag):
        try:
            text = bs4_string(tag)
            if text is None:
                self.itunes_duration = None
                return
            time_no_mil = text.split(".")
            t = time_no_mil[0].split(":")
            duration = 0
            if len(t) == 3:
                duration += int(t[0]) * 3600
                duration += int(t[1]) * 60
                duration += int(t[2])
                self.itunes_duration = duration
            elif len(t) == 2:
                duration += int(t[0]) * 60
                duration += int(t[1])
                self.itunes_duration = duration
            else:
                self.itunes_duration = text
        except AttributeError:
            self.itunes_duration = None
        except Exception:
            raise InvalidPodcastFeed(
                f"Invalid Podcast Feed, episode level itunes:duration: {bs4_string(tag)}, could not be parsed"
            )

    def set_itunes_explicit(self, tag):
        try:
            text = bs4_string(tag)
            if text is None:
                self.itunes_explicit = None
                return
            self.itunes_explicit = text
            lowered = self.itunes_explicit.lower()
            if lowered in ("no", "false", "clean"):
                self.itunes_explicit = False
            elif lowered in ("yes", "true") or "offensive" in lowered:
                self.itunes_explicit = True
            else:
                self.itunes_explicit = None
        except AttributeError:
            self.itunes_explicit = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level itunes:explicit could not be parsed"
            )

    def set_itunes_image(self, tag):
        try:
            self.itunes_image = tag.get("href")
        except AttributeError:
            self.itunes_image = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level itunes:image could not be parsed"
            )

    def set_itunes_order(self, tag):
        try:
            text = bs4_string(tag)
            self.itunes_order = text.lower() if text else None
        except AttributeError:
            self.itunes_order = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level itunes:order could not be parsed"
            )

    def set_itunes_subtitle(self, tag):
        try:
            self.itunes_subtitle = bs4_string(tag)
        except AttributeError:
            self.itunes_subtitle = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level itunes:subtitle could not be parsed"
            )

    def set_itunes_summary(self, tag):
        try:
            self.itunes_summary = bs4_string(tag)
        except AttributeError:
            self.itunes_summary = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level itunes:summary could not be parsed"
            )

    def set_interactive(self, tag):
        try:
            text = bs4_string(tag)
            self.interactive = (text or "").lower() == "yes"
            self.is_interactive = self.interactive
        except AttributeError:
            self.interactive = False
            self.is_interactive = self.interactive
        except Exception:
            raise InvalidPodcastFeed(
                f"Invalid Podcast Feed, episode level ihr:interactive: {bs4_string(tag)}, could not be parsed"
            )

    def set_alternate_enclosure(self, tag):
        """Parses podcast:alternateEnclosure and its nested podcast:source elements."""
        try:
            enclosure_dict = {}

            enclosure_dict["mime_type"] = tag.get("type")

            enclosure_dict["length"] = tag.get("length")
            if enclosure_dict["length"]:
                try:
                    enclosure_dict["length"] = int(enclosure_dict["length"])
                except (ValueError, TypeError):
                    pass

            enclosure_dict["bitrate"] = tag.get("bitrate")
            if enclosure_dict["bitrate"]:
                try:
                    enclosure_dict["bitrate"] = float(enclosure_dict["bitrate"])
                except (ValueError, TypeError):
                    pass

            enclosure_dict["height"] = tag.get("height")
            if enclosure_dict["height"]:
                try:
                    enclosure_dict["height"] = int(enclosure_dict["height"])
                except (ValueError, TypeError):
                    pass

            enclosure_dict["lang"] = tag.get("lang")
            enclosure_dict["title"] = tag.get("title")
            enclosure_dict["rel"] = tag.get("rel")
            enclosure_dict["codecs"] = tag.get("codecs")

            default_value = tag.get("default", "False")
            falsy_strings = ("false", "0", "no", "False")
            enclosure_dict["default"] = default_value.lower() not in falsy_strings

            # Direct children only; accept both unprefixed <source> and
            # <podcast:source>, matching BS4 filter `prefix == "podcast" or not prefix`.
            sources = []
            for source_tag in tag.iterchildren(tag=etree.Element):
                prefix, name = _qname(source_tag.tag, self._prefix_map)
                if name == "source" and (prefix == "podcast" or prefix is None):
                    source_dict = {
                        "uri": source_tag.get("uri") or source_tag.get("url"),
                        "content_type": source_tag.get("contentType"),
                        "integrity_type": None,
                        "integrity_value": None,
                    }
                    sources.append(source_dict)

            for integrity_tag in tag.iterchildren(tag=etree.Element):
                prefix, name = _qname(integrity_tag.tag, self._prefix_map)
                if name == "integrity" and (prefix == "podcast" or prefix is None) and sources:
                    integrity_type = integrity_tag.get("type")
                    integrity_value = integrity_tag.get("value")
                    for source in sources:
                        source["integrity_type"] = integrity_type
                        source["integrity_value"] = integrity_value

            enclosure_dict["sources"] = sources

            self.alternate_enclosures.append(enclosure_dict)

        except AttributeError:
            pass
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level podcast:alternateEnclosure could not be parsed"
            )
