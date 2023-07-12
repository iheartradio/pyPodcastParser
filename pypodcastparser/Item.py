from bs4 import Tag

import datetime
from datetime import timezone
import email.utils
import re
import pytz
import logging

LOGGER = logging.getLogger(__name__)


pytz_timezon_list = [tz for tz in pytz.all_timezones]
common_timezones = {
    "GMT": "GMT",
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
}


class Item(object):
    """Parses an xml rss feed

    RSS Specs http://cyber.law.harvard.edu/rss/rss.html
    iTunes Podcast Specs http://www.apple.com/itunes/podcasts/specs.html

    Args:
        soup (bs4.BeautifulSoup): BeautifulSoup object representing a rss item

    Note:
        All attributes with empty or nonexistent element
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
        }

        # Populate attributes based on feed content
        for c in self.soup.children:
            if not isinstance(c, Tag):
                continue
            try:
                # Using get instead of pop since there can be multiple transcript tags (meaning we don't want to get rid of method after use)
                if c.name == "transcript":
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

    def set_dates_published(self):
        if self.time_published is None:
            self.date_time = None
            return
        try:
            self.date_time = datetime.date.fromtimestamp(self.time_published)
        except ValueError:
            self.date_time = None

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
        item["transcription"] = self.podcast_transcript

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

    def set_description(self, tag):
        """Parses description and set value."""
        try:
            self.description = tag.string
        except AttributeError:
            self.description = None

    def set_content_encoded(self, tag):
        """Parses content_encoded and set value."""
        try:
            self.content_encoded = tag.string
            if self.description == None:
                self.description = self.content_encoded
        except AttributeError:
            self.content_encoded = None

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

    # TODO convert to one timezone
    def set_published_date(self, tag):
        """Parses published date and set value."""
        try:
            self.published_date = tag.string
            self.published_date_string = tag.string

            deconstructed_date = self.published_date_string.split(" ")
            if len(deconstructed_date) < 4:
                raise AttributeError

            published_date_timezone = ""
            if re.match("^[a-zA-Z]{3}$", deconstructed_date[-1]):
                published_date_timezone = deconstructed_date[-1]
                deconstructed_date.pop()
            elif "+1000" in self.published_date:
                published_date_timezone = "AEST"
                deconstructed_date.pop()
            else:
                published_date_timezone = "EST"

            regex_array = [
                "^[a-zA-Z]{3},$",
                "^\d{1,2}$",
                "^[a-zA-Z]{3}$",
                "^\d{4}$",
                "^\d\d:\d\d",
            ]
            new_array = []
            for array_index, array_value in enumerate(regex_array):
                if re.match(deconstructed_date[array_index], array_value):
                    new_array.append(array_value)
                else:
                    for inner_index, inner_value in enumerate(deconstructed_date):
                        if re.match(regex_array[array_index], inner_value):
                            new_array.append(inner_value)
                            break
            date_string = (
                new_array[0]
                + " "
                + new_array[1]
                + " "
                + new_array[2]
                + " "
                + new_array[3]
                + " "
                + new_array[4]
            )

            if len(new_array) != 5:
                raise AttributeError(
                    "Error creating new date array. Array is not of length 5 for formatting"
                )

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
                now = datetime.datetime.now(timezone.utc)
                published_date_timezone = "UTC"
                self.published_date = datetime.datetime.strptime(
                    now, "%a, %d %b %Y %H:%M:%S"
                )

            if published_date_timezone not in ["ET", "EST", "EDT"]:
                if published_date_timezone in pytz_timezon_list:
                    current_timezone = pytz.timezone(published_date_timezone)
                else:
                    current_timezone = pytz.timezone(
                        common_timezones.get(published_date_timezone)
                    )

                date_in_current_timezone = current_timezone.localize(
                    self.published_date
                )
                self.published_date = str(
                    (
                        date_in_current_timezone.astimezone(pytz.timezone("US/Eastern"))
                    ).replace(tzinfo=None)
                )
                LOGGER.info("Final Published Date EST: {}".format(self.published_date))
            else:
                LOGGER.info("Final Published Date EST: {}".format(self.published_date))

        except Exception:
            self.published_date = datetime.datetime.now(
                pytz.timezone("US/Eastern")
            ).strftime("%Y-%m-%d %H:%M")

    def set_title(self, tag):
        """Parses title and set value."""
        try:
            self.title = tag.string
        except AttributeError:
            self.title = None

    def set_itunes_author_name(self, tag):
        """Parses author name from itunes tags and sets value"""
        try:
            self.itunes_author_name = tag.string
        except AttributeError:
            self.itunes_author_name = None

    def set_itunes_episode(self, tag):
        """Parses the episode number and sets value"""
        try:
            self.itunes_episode = tag.string

            if self.itunes_episode == "" or self.itunes_episode == None:
                self.itunes_episode = "0"
        except AttributeError:
            self.itunes_episode = "0"

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

    def set_itunes_block(self, tag):
        """Check and see if item is blocked from iTunes and sets value"""
        try:
            block = tag.string.lower()
        except AttributeError:
            block = ""
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

    def set_itunes_image(self, tag):
        """Parses itunes item images and set url as value"""
        try:
            self.itunes_image = tag.get("href")
        except AttributeError:
            self.itunes_image = None

    def set_itunes_order(self, tag):
        """Parses episode order and set url as value"""
        try:
            self.itunes_order = tag.string
            self.itunes_order = self.itunes_order.lower()
        except AttributeError:
            self.itunes_order = None

    def set_itunes_subtitle(self, tag):
        """Parses subtitle from itunes tags and sets value"""
        try:
            self.itunes_subtitle = tag.string
        except AttributeError:
            self.itunes_subtitle = None

    def set_itunes_summary(self, tag):
        """Parses summary from itunes tags and sets value"""
        try:
            self.itunes_summary = tag.string
        except AttributeError:
            self.itunes_summary = None

    def set_interactive(self, tag):
        """Parses author and set value."""
        try:
            self.interactive = tag.string.lower() == "yes"
            self.is_interactive = self.interactive
        except AttributeError:
            self.interactive = False
            self.is_interactive = self.interactive
