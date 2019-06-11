# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup, Tag
from datetime import datetime, date
import email.utils
from time import mktime
import time

from pyPodcastParser.Item import Item

class InvalidPodcastFeed(ValueError):
    pass

class Podcast():
    """Parses an xml rss feed

    RSS Specs http://cyber.law.harvard.edu/rss/rss.html

    More RSS Specs http://www.rssboard.org/rss-specification

    iTunes Podcast Specs http://www.apple.com/itunes/podcasts/specs.html


    The cloud element aka RSS Cloud is not supported as it has been superseded by the superior PubSubHubbub protocal

    Args:
        feed_content (str): An rss string

    Note:
        All attributes with empty or nonexistent element will have a value of None

        Attributes are generally strings or lists of strings, because we want to record the literal value of elements.

    Attributes:
        feed_content (str): The actual xml of the feed
        soup (bs4.BeautifulSoup): A soup of the xml with items and image removed
        copyright (str): The feed's copyright
        items (item): Item objects
        description (str): The feed's description
        image_url (str): Feed image url
        itunes_author_name (str): The podcast's author name for iTunes
        itunes_block (bool): Does the podcast block itunes
        itunes_categories (list): List of strings of itunes categories
        itunes_complete (str): Is this podcast done and complete
        itunes_explicit (str): Is this item explicit. Should only be "yes" and "clean."
        itunes_image (str): URL to itunes image
        itunes_new_feed_url (str): The new url of this podcast
        language (str): Language of feed
        last_build_date (str): Last build date of this feed
        link (str): URL to homepage
        published_date (str): Date feed was published
        owner_name (str): Name of feed owner
        owner_email (str): Email of feed owner
        subtitle (str): The feed subtitle
        title (str): The feed title
        date_time (datetime): When published
    """

    def __init__(self, feed_content):
        self.feed_content = feed_content
        self.items = []
        self.itunes_categories = []

        # Initialize attributes as they might not be populated
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
        self.summary = None
        self.owner_name = None
        self.owner_email = None
        self.subtitle = None
        self.title = None
        self.date_time = None
        self.itunes_type = None

        self.set_soup()
        tag_methods = {
            (None, 'copyright'): self.set_copyright,
            (None, 'description'): self.set_description,
            (None, 'image'): self.set_image,
            (None, 'language'): self.set_language,
            (None, 'lastBuildDate'): self.set_last_build_date,
            (None, 'link'): self.set_link,
            (None, 'pubDate'): self.set_published_date,
            (None, 'title'): self.set_title,
            (None, 'item'): self.add_item,
            ('itunes', 'author'): self.set_itunes_author_name,
            ('itunes', 'type'): self.set_itunes_type,
            ('itunes', 'block'): self.set_itunes_block,
            ('itunes', 'category'): self.add_itunes_category,
            ('itunes', 'complete'): self.set_itunes_complete,
            ('itunes', 'explicit'): self.set_itunes_explicit,
            ('itunes', 'image'): self.set_itunes_image,
            ('itunes', 'new-feed-url'): self.set_itunes_new_feed_url,
            ('itunes', 'owner'): self.set_owner,
            ('itunes', 'subtitle'): self.set_subtitle,
            ('itunes', 'summary'): self.set_summary,
        }
        many_tag_methods = set([ (None, 'item'), ('itunes', 'category')])

        try:
            channel = self.soup.rss.channel
        except AttributeError:
            raise InvalidPodcastFeed('Invalid Podcast Feed')

        # Populate attributes based on feed content
        for c in channel.children:
            if not isinstance(c, Tag):
                continue
            try:
                # Pop method to skip duplicated tag on invalid feeds
                tag_tuple = (c.prefix, c.name)
                if tag_tuple in many_tag_methods:
                    tag_method = tag_methods[tag_tuple]
                else:
                    tag_method = tag_methods.pop(tag_tuple)
            except (AttributeError, KeyError):
                continue

            tag_method(c)

        self.set_time_published()
        self.set_dates_published()

    def set_time_published(self):
        if self.published_date is None:
            self.time_published = None
            return
        time_tuple = email.utils.parsedate_tz(self.published_date)
        try:
            self.time_published = email.utils.mktime_tz(time_tuple)
        except TypeError:
            self.time_published = None

    def set_dates_published(self):
        if self.time_published is None:
            self.date_time = None
        else:
            self.date_time = date.fromtimestamp(self.time_published)

    def to_dict(self):
        podcast_dict = {}
        podcast_dict['copyright'] = self.copyright
        podcast_dict['description'] = self.description
        podcast_dict['image_url'] = self.image_url
        podcast_dict['image_link'] = self.image_link
        podcast_dict['items'] = []
        for item in self.items:
            item_dict = item.to_dict()
            podcast_dict['items'].append(item_dict)
        podcast_dict['itunes_author_name'] = self.itunes_author_name
        podcast_dict['itunes_block'] = self.itunes_block
        podcast_dict['itunes_categories'] = self.itunes_categories
        podcast_dict['itunes_block'] = self.itunes_block
        podcast_dict['itunes_complete'] = self.image_width
        podcast_dict['itunes_explicit'] = self.itunes_explicit
        podcast_dict['itunes_image'] = self.itunes_image
        podcast_dict['itunes_explicit'] = self.itunes_explicit
        podcast_dict['itunes_new_feed_url'] = self.itunes_new_feed_url
        podcast_dict['language'] = self.language
        podcast_dict['last_build_date'] = self.last_build_date
        podcast_dict['link'] = self.link
        podcast_dict['published_date'] = self.published_date
        podcast_dict['owner_name'] = self.owner_name
        podcast_dict['owner_email'] = self.owner_email
        podcast_dict['subtitle'] = self.subtitle
        podcast_dict['title'] = self.title
        podcast_dict['type'] = self.type
        return podcast_dict

    def set_soup(self):
        """Sets soup and strips items"""
        self.soup = BeautifulSoup(self.feed_content, features="lxml-xml")

    def add_item(self, tag):
        item = Item(tag)
        self.items.append(item)

    def set_copyright(self, tag):
        """Parses copyright and set value"""
        try:
            self.copyright = tag.string
        except AttributeError:
            self.copyright = None

    def set_description(self, tag):
        """Parses description and sets value"""
        try:
            self.description = tag.string
        except AttributeError:
            self.description = None

    def set_image(self, tag):
        """Parses image element and set values"""
        try:
            self.image_url = tag.find('url', recursive=False).string
        except AttributeError:
            self.image_url = None

    def set_itunes_author_name(self, tag):
        """Parses author name from itunes tags and sets value"""
        try:
            self.itunes_author_name = tag.string
        except AttributeError:
            self.itunes_author_name = None

    def set_itunes_type(self, tag):
        """Parses the type of show and sets value"""
        try:
            self.itunes_type = tag.string
        except AttributeError:
            self.itunes_type = None

    def set_itunes_block(self, tag):
        """Check and see if podcast is blocked from iTunes and sets value"""
        try:
            block = tag.string.lower()
        except AttributeError:
            block = ""
        if block == "yes":
            self.itunes_block = True
        else:
            self.itunes_block = False

    def add_itunes_category(self, tag):
        """Parses and add itunes category"""
        category_text = tag.get('text')
        self.itunes_categories.append(category_text)

    def set_itunes_complete(self, tag):
        """Parses complete from itunes tags and sets value"""
        try:
            self.itunes_complete = tag.string.lower()
        except AttributeError:
            self.itunes_complete = None

    def set_itunes_explicit(self, tag):
        """Parses explicit from itunes tags and sets value"""
        try:
            self.itunes_explicit = tag.string.lower()
        except AttributeError:
            self.itunes_explicit = None

    def set_itunes_image(self, tag):
        """Parses itunes images and set url as value"""
        try:
            self.itunes_image = tag.get('href')
        except AttributeError:
            self.itunes_image = None

    def set_itunes_new_feed_url(self, tag):
        """Parses new feed url from itunes tags and sets value"""
        try:
            self.itunes_new_feed_url = tag.string
        except AttributeError:
            self.itunes_new_feed_url = None

    def set_language(self, tag):
        """Parses feed language and set value"""
        try:
            self.language = tag.string
        except AttributeError:
            self.language = None

    def set_last_build_date(self, tag):
        """Parses last build date and set value"""
        try:
            self.last_build_date = tag.string
        except AttributeError:
            self.last_build_date = None

    def set_link(self, tag):
        """Parses link to homepage and set value"""
        try:
            self.link = tag.string
        except AttributeError:
            self.link = None

    def set_published_date(self, tag):
        """Parses published date and set value"""
        try:
            self.published_date = tag.string
        except AttributeError:
            self.published_date = None

    def set_owner(self, tag):
        """Parses owner name and email then sets value"""
        try:
            self.owner_name = tag.find('itunes:name', recursive=False).string
        except AttributeError:
            self.owner_name = None
        try:
            self.owner_email = tag.find('itunes:email', recursive=False).string
        except AttributeError:
            self.owner_email = None

    def set_subtitle(self, tag):
        """Parses subtitle and sets value"""
        try:
            self.subtitle = tag.string
        except AttributeError:
            self.subtitle = None

    def set_summary(self, tag):
        """Parses summary and set value"""
        try:
            self.summary = tag.string
        except AttributeError:
            self.summary = None

    def set_title(self, tag):
        """Parses title and set value"""
        try:
            self.title = tag.string
        except AttributeError:
            self.title = None
