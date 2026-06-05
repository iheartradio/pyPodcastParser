from bs4 import Tag

import datetime
import email.utils
import logging

from dateutil import parser as _dateutil_parser, tz as _dateutil_tz

from pypodcastparser.Error import InvalidPodcastFeed


LOGGER = logging.getLogger(__name__)


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

# dateutil tzinfos: lets `dateutil.parser.parse` resolve abbreviations like
# "EDT" / "PST" that it doesn't ship with by default. GMT/UTC and numeric
# offsets (e.g. "+1000", "-0500") are handled natively, so they're not
# listed here.
_TZ_INFOS = {abbrev: _dateutil_tz.gettz(iana) for abbrev, iana in common_timezones.items()}
# RFC 2822 daylight-saving abbreviations that aren't in common_timezones.
# Each maps to its DST-aware IANA zone so localizing a date during DST
# yields the correct UTC offset.
_TZ_INFOS.setdefault("EDT", _dateutil_tz.gettz("US/Eastern"))
_TZ_INFOS.setdefault("ET", _dateutil_tz.gettz("US/Eastern"))
_TZ_INFOS.setdefault("CDT", _dateutil_tz.gettz("US/Central"))
_TZ_INFOS.setdefault("MDT", _dateutil_tz.gettz("America/Denver"))

_US_EASTERN = _dateutil_tz.gettz("US/Eastern")


class Item(object):
    """Parses an xml rss feed

    RSS Specs http://cyber.law.harvard.edu/rss/rss.html
    iTunes Podcast Specs http://www.apple.com/itunes/podcasts/specs.html

    Args:
        soup (bs4.BeautifulSoup): BeautifulSoup object representing a rss item

    Note:
        All attributes with empty or non-existent element
        will have a value of None

    Attributes:
        author (str): The author of the item
        description (str): Description of the item.
        enclosure_url (str): URL of enclosure
        enclosure_type (str): File MIME type
        enclosure_length (int): File size in bytes
        guid (str): globally unique identifier
        itunes_author_name (str): Author name given to iTunes
        itunes_episode_type (srt): Itunes episode type
        itunes_episode (int): Episode number in season
        itunes_season (int): Podcast season
        itunes_block (bool): It this Item blocked from itunes
        itunes_duration (str): Duration of enclosure
        itunes_explicit (str): Is this item explicit.
        Should only be yes or clean.
        itunes_image (str): URL of item cover art
        itunes_order (str): Override published_date order
        itunes_subtitle (str): The item subtitle
        itunes_summary (str): The summary of the item
        content_encoded(str): The encoded content of the item
        published_date (str): Date item was published
        title (str): The title of item.
        interactive(bool): This item is interactive
        is_interactive (boolean): Is an iheart podcast interactive
    """

    def __init__(self, soup):
        self.soup = soup

        # Initialize attributes as they might not be populated
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

        # Populate attributes based on feed content
        for c in self.soup.children:
            if not isinstance(c, Tag):
                continue
            try:
                # Using get instead of pop since there can be multiple transcript tags (meaning we don't want to get rid of method after use)
                if c.name == "transcript" or c.name == "alternateEnclosure":
                    tag_method = tag_methods.get((c.prefix, c.name))
                else:
                    # Pop method to skip duplicated tag on invalid feeds
                    tag_method = tag_methods.pop((c.prefix, c.name))
            except (AttributeError, KeyError):
                continue

            tag_method(c)

        self.set_time_published()
        self.set_dates_published()

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
        item = {}
        item["external_id"] = self.guid
        item["episode_duration"] = self.itunes_duration
        item["is_explicit"] = self.itunes_explicit
        item["episode_number"] = self.itunes_episode
        item["episode_season"] = self.itunes_season
        item["episode_type"] = self.itunes_episode_type
        item["external_image_url"] = self.itunes_image
        item["episode_subtitle"] = self.itunes_subtitle
        item["episode_description"] = self.description
        item["original_air_date"] = self.published_date
        item["start_date"] = self.published_date
        item["episode_title"] = self.title
        item["interactive"] = self.interactive
        item["external_url"] = self.enclosure_url
        item["enclosure_type"] = self.enclosure_type
        item["enclosure_length"] = self.enclosure_length
        item["transcription"] = self.podcast_transcript
        item["alternate_enclosures"] = self.alternate_enclosures

        return item

    def set_rss_element(self):
        """Set each of the basic rss elements."""
        self.set_enclosure()

    def set_author(self, tag):
        """Parses author and set value."""
        try:
            self.author = tag.string
        except AttributeError:
            self.author = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level author could not be parsed"
            )

    def set_description(self, tag):
        """Parses description and set value."""
        try:
            self.description = tag.string
        except AttributeError:
            self.description = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level description could not be parsed"
            )

    def set_content_encoded(self, tag):
        """Parses content_encoded and set value."""
        try:
            self.content_encoded = tag.string
            if self.description == None:
                self.description = self.content_encoded
        except AttributeError:
            self.content_encoded = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level content_encoded could not be parsed"
            )

    def set_enclosure(self, tag):
        """Parses enclosure_url, enclosure_type then set values."""
        try:
            self.enclosure_url = tag["url"]
        except Exception:
            self.enclosure_url = None
        try:
            self.enclosure_type = tag["type"]
        except Exception:
            self.enclosure_type = None
        try:
            self.enclosure_length = tag["length"]
            self.enclosure_length = int(self.enclosure_length)
        except Exception:
            self.enclosure_length = None

    def set_guid(self, tag):
        """Parses guid and set value"""
        try:
            self.guid = tag.string
        except AttributeError:
            self.guid = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level guid could not be parsed"
            )

    def set_published_date(self, tag):
        """Parses item-level published date, normalizes to US/Eastern,
        and stores as a naive wall-clock string ("YYYY-MM-DD HH:MM:SS").

        On any parse failure, falls back to the current US/Eastern time —
        matches legacy behavior so downstream consumers always get *a*
        date even when the feed's pubDate is malformed.
        """
        text = tag.string
        if text is None:
            return
        self.published_date = text
        self.published_date_string = text
        try:
            parsed = _dateutil_parser.parse(text, tzinfos=_TZ_INFOS)
            # No tz in the input → default to EST, mirroring legacy.
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=_US_EASTERN)
            normalized = parsed.astimezone(_US_EASTERN).replace(tzinfo=None)
            self.published_date = str(normalized)
            LOGGER.info("Final Published Date EST: %s", self.published_date)
        except (ValueError, TypeError, OverflowError, _dateutil_parser.ParserError):
            self.published_date = datetime.datetime.now(_US_EASTERN).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

    def set_title(self, tag):
        """Parses title and set value."""
        try:
            self.title = tag.string
        except AttributeError:
            self.title = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level title could not be parsed"
            )

    def set_itunes_author_name(self, tag):
        """Parses author name from itunes tags and sets value"""
        try:
            self.itunes_author_name = tag.string
        except AttributeError:
            self.itunes_author_name = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level itunes:author could not be parsed"
            )

    def set_itunes_episode(self, tag):
        """Parses the episode number and sets value"""
        try:
            self.itunes_episode = tag.string

            if self.itunes_episode == "" or self.itunes_episode == None:
                self.itunes_episode = "0"
        except AttributeError:
            self.itunes_episode = "0"
        except Exception:
            raise InvalidPodcastFeed(
                f"Invalid Podcast Feed, episode level itunes:episode: {tag.string}, could not be parsed"
            )

    def set_podcast_transcript(self, tag):
        """Parses the episode transcript and sets value
        If there are multiple transcripts, it will get the one with the highest quality, i.e: text/plain,
        otherwise it will get the most recently read one (the last one in the list)
        """
        try:
            transcript_dict = {}
            transcript_dict["url"] = tag.get("url", None)
            transcript_dict["type"] = tag.get("type", None)
            transcript_dict["language"] = tag.get("language", None)
            transcript_dict["rel"] = tag.get("rel", None)
            self.transcriptionList.append(transcript_dict)
            self.podcast_transcript = self.transcriptionList
        except AttributeError:
            self.podcast_transcript = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode transcription could not be parsed"
            )

    def set_itunes_season(self, tag):
        """Parses the episode season and sets value"""
        try:
            self.itunes_season = tag.string
            if self.itunes_season == "" or self.itunes_season == None:
                self.itunes_season = "0"
        except AttributeError:
            self.itunes_season = "0"

    def set_itunes_episode_type(self, tag):
        """Parses the episode type and sets value"""
        try:
            self.itunes_episode_type = tag.string
            self.itunes_episode_type = self.itunes_episode_type.lower()
        except AttributeError:
            self.itunes_episode_type = None
        except Exception:
            raise InvalidPodcastFeed(
                f"Invalid Podcast Feed, episode level itunes:episodeType: {tag.string}, could not be parsed"
            )

    def set_itunes_block(self, tag):
        """Check and see if item is blocked from iTunes and sets value"""
        try:
            block = tag.string.lower()
        except AttributeError:
            block = ""
        except Exception:
            raise InvalidPodcastFeed(
                f"Invalid Podcast Feed, episode level itunes:block: {tag.string}, could not be parsed"
            )
        if block == "yes":
            self.itunes_block = True
        else:
            self.itunes_block = False

    def set_itunes_duration(self, tag):
        """Parses duration from itunes tags and sets value"""
        try:
            # remove milli seconds
            time_no_mil = tag.string.split(".")
            t = time_no_mil[0].split(":")
            duration = 0
            if len(t) == 3:
                for i, v in enumerate(t):
                    if i == 0:
                        duration += int(t[0]) * 3600
                    elif i == 1:
                        duration += int(t[1]) * 60
                    else:
                        duration += int(t[2])
                self.itunes_duration = duration

            elif len(t) == 2:
                for i, v in enumerate(t):
                    if i == 0:
                        duration += int(t[0]) * 60
                    else:
                        duration += int(t[1])

                self.itunes_duration = duration
            else:
                self.itunes_duration = tag.string

        except AttributeError:
            self.itunes_duration = None
        except Exception:
            raise InvalidPodcastFeed(
                f"Invalid Podcast Feed, episode level itunes:duration: {tag.string}, could not be parsed"
            )

    def set_itunes_explicit(self, tag):
        """Parses explicit from itunes item tags and sets value"""
        try:
            self.itunes_explicit = tag.string
            if (
                self.itunes_explicit.lower() == "no"
                or self.itunes_explicit.lower() == "false"
                or self.itunes_explicit.lower() == "clean"
            ):
                self.itunes_explicit = False
            elif (
                self.itunes_explicit.lower() == "yes"
                or self.itunes_explicit.lower() == "true"
                or "offensive" in self.itunes_explicit.lower()
            ):
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
        """Parses itunes item images and set url as value"""
        try:
            self.itunes_image = tag.get("href")
        except AttributeError:
            self.itunes_image = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level itunes:image could not be parsed"
            )

    def set_itunes_order(self, tag):
        """Parses episode order and set url as value"""
        try:
            self.itunes_order = tag.string
            self.itunes_order = self.itunes_order.lower()
        except AttributeError:
            self.itunes_order = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level itunes:order could not be parsed"
            )

    def set_itunes_subtitle(self, tag):
        """Parses subtitle from itunes tags and sets value"""
        try:
            self.itunes_subtitle = tag.string
        except AttributeError:
            self.itunes_subtitle = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level itunes:subtitle could not be parsed"
            )

    def set_itunes_summary(self, tag):
        """Parses summary from itunes tags and sets value"""
        try:
            self.itunes_summary = tag.string
        except AttributeError:
            self.itunes_summary = None
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level itunes:summary could not be parsed"
            )

    def set_interactive(self, tag):
        """Parses author and set value."""
        try:
            self.interactive = tag.string.lower() == "yes"
            self.is_interactive = self.interactive
        except AttributeError:
            self.interactive = False
            self.is_interactive = self.interactive
        except Exception:
            raise InvalidPodcastFeed(
                f"Invalid Podcast Feed, episode level ihr:interactive: {tag.string}, could not be parsed"
            )

    def set_alternate_enclosure(self, tag):
        """Parses podcast:alternateEnclosure and its nested podcast:source elements.

        The alternateEnclosure element provides alternative media versions with different
        formats, quality levels, and transport methods (HTTPS, IPFS, torrents, etc.).
        """
        try:
            enclosure_dict = {}

            # Parse main alternateEnclosure attributes
            enclosure_dict["mime_type"] = tag.get("type", None)
            enclosure_dict["length"] = tag.get("length", None)
            if enclosure_dict["length"]:
                try:
                    enclosure_dict["length"] = int(enclosure_dict["length"])
                except (ValueError, TypeError):
                    pass

            enclosure_dict["bitrate"] = tag.get("bitrate", None)
            if enclosure_dict["bitrate"]:
                try:
                    enclosure_dict["bitrate"] = float(enclosure_dict["bitrate"])
                except (ValueError, TypeError):
                    pass

            enclosure_dict["height"] = tag.get("height", None)
            if enclosure_dict["height"]:
                try:
                    enclosure_dict["height"] = int(enclosure_dict["height"])
                except (ValueError, TypeError):
                    pass

            enclosure_dict["lang"] = tag.get("lang", None)
            enclosure_dict["title"] = tag.get("title", None)
            enclosure_dict["rel"] = tag.get("rel", None)
            enclosure_dict["codecs"] = tag.get("codecs", None)

            # Parse default attribute as boolean
            default_value = tag.get("default", "False")
            falsy_strings = ("false", "0", "no", "False")
            enclosure_dict["default"] = default_value.lower() not in falsy_strings

            # Parse nested podcast:source elements
            sources = []
            for source_tag in tag.find_all("source", recursive=False):
                if source_tag.prefix == "podcast" or not source_tag.prefix:
                    source_dict = {}
                    # Support both 'uri' (spec) and 'url' (some feeds use this)
                    source_dict["uri"] = source_tag.get("uri", None) or source_tag.get("url", None)
                    source_dict["content_type"] = source_tag.get("contentType", None)
                    source_dict["integrity_type"] = None
                    source_dict["integrity_value"] = None
                    sources.append(source_dict)

            # Parse podcast:integrity elements and add to all sources (applies to the content itself)
            for integrity_tag in tag.find_all("integrity", recursive=False):
                if (integrity_tag.prefix == "podcast" or not integrity_tag.prefix) and len(sources) > 0:
                    integrity_type = integrity_tag.get("type", None)
                    integrity_value = integrity_tag.get("value", None)
                    # Add integrity to all sources since it applies to the media content
                    for source in sources:
                        source["integrity_type"] = integrity_type
                        source["integrity_value"] = integrity_value

            enclosure_dict["sources"] = sources

            self.alternate_enclosures.append(enclosure_dict)

        except AttributeError:
            # If there's an issue parsing, we don't add it to the list
            pass
        except Exception:
            raise InvalidPodcastFeed(
                "Invalid Podcast Feed, episode level podcast:alternateEnclosure could not be parsed"
            )
