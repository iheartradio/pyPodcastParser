from bs4 import Tag

import datetime
import email.utils
from dateutil.parser import parse
import re
import time
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

        tag_methods = {
            (None, 'title'): self.set_title,
            (None, 'author'): self.set_author,
            (None, 'description'): self.set_description,
            (None, 'guid'): self.set_guid,
            (None, 'pubDate'): self.set_published_date,
            (None, 'enclosure'): self.set_enclosure,
            (None, 'is_interactive'): self.is_interactive,
            ('content', 'encoded'): self.set_content_encoded,
            ('itunes', 'author'): self.set_itunes_author_name,
            ('itunes', 'episode'): self.set_itunes_episode,
            ('itunes', 'episodeType'): self.set_itunes_episode_type,
            ('itunes', 'block'): self.set_itunes_block,
            ('itunes', 'season'): self.set_itunes_season,
            ('itunes', 'duration'): self.set_itunes_duration,
            ('itunes', 'explicit'): self.set_itunes_explicit,
            ('itunes', 'image'): self.set_itunes_image,
            ('itunes', 'order'): self.set_itunes_order,
            ('itunes', 'subtitle'): self.set_itunes_subtitle,
            ('itunes', 'summary'): self.set_itunes_summary,
            ('ihr', 'interactive'): self.set_interactive,

        }

        # Populate attributes based on feed content
        for c in self.soup.children:
            if not isinstance(c, Tag):
                continue
            try:
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
        item['external_id'] = self.guid
        item['episode_duration'] = self.itunes_duration
        item['is_explicit'] = self.itunes_explicit
        item['episode_number'] = self.itunes_episode
        item['episode_season'] = self.itunes_season
        item['episode_type'] = self.itunes_episode_type
        item['external_image_url'] = self.itunes_image
        item['episode_subtitle'] = self.itunes_subtitle
        item['episode_description'] = self.description
        item['original_air_date'] = self.published_date
        item['start_date'] = self.published_date
        item['episode_title'] = self.title
        item['interactive'] = self.interactive
        item['external_url'] = self.enclosure_url


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
        except AttributeError:
            self.content_encoded = None

    def set_enclosure(self, tag):
        """Parses enclosure_url, enclosure_type then set values."""
        try:
            self.enclosure_url = tag['url']
        except Exception:
            self.enclosure_url = None
        try:
            self.enclosure_type = tag['type']
        except Exception:
            self.enclosure_type = None
        try:
            self.enclosure_length = tag['length']
            self.enclosure_length = int(self.enclosure_length)
        except Exception:
            self.enclosure_length = None

    def set_guid(self, tag):
        """Parses guid and set value"""
        try:
            self.guid = tag.string
        except AttributeError:
            self.guid = None

    def set_published_date(self, tag):
        """Parses published date and set value."""
        try:
            self.published_date = tag.string
            self.published_date_string = tag.string
            a = tag.string.split(":")
            b = a[2]
            seconds = b[:2]
            a[0] += ":"+a[1]
            a[0] += ":"+seconds

            self.published_date = str(datetime.datetime.strptime(a[0], "%a, %d %b %Y %H:%M:%S"))
        except AttributeError:
            self.published_date = None

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
            if -32767 > self.itunes_episode or self.itunes_episode > 32767 or self.itunes_episode == None:
                self.itunes_episode = 0
        except AttributeError:
            self.itunes_episode = None

    def set_itunes_season(self, tag):
        """Parses the episode season and sets value"""
        try:
            self.itunes_season = tag.string
            if -32767 > self.itunes_season or self.itunes_season > 32767 or self.itunes_season == None:
		        self.itunes_season = 0
        except AttributeError:
            self.itunes_season = None

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
            #remove milli seconds
            time_no_mil = tag.string.split('.')
            t = time_no_mil[0].split(':')
            duration = 0
            if(len(t) == 3):
                for i,v in enumerate(t):
                    if(i  == 0):
                        duration += int(t[0]) * 3600
                    elif(i  == 1):
                        duration += int(t[1]) * 60
                    else:
                        duration += int(t[2])
                self.itunes_duration = duration

            elif(len(t) == 2):
                for i,v in enumerate(t):
                    if(i  == 0):
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
            if(self.itunes_explicit.lower() == 'no'):
                self.itunes_explicit = False
            elif(self.itunes_explicit.lower() == 'yes'):
                self.itunes_explicit = True
            else:
                self.itunes_explicit = self.itunes_explicit.lower()

        except AttributeError:
            self.itunes_explicit = None

    def set_itunes_image(self, tag):
        """Parses itunes item images and set url as value"""
        try:
            self.itunes_image = tag.get('href')
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
            self.interactive = (tag.string.lower() == "yes")
            self.is_interactive = self.interactive
        except AttributeError:
            self.interactive = False
            self.is_interactive = self.interactive
