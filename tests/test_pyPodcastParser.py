# -*- coding: utf-8 -*-
import datetime
import os
import unittest

from pypodcastparser import Podcast

# py.test test_pypodcastparser.py

#######
# coverage run --source pypodcastparser -m py.test
#######
# py.test --cov=pypodcastparser tests/
#######
# py.test -v   --capture=sys tests/test_pypodcastparser.py


class TestTest(unittest.TestCase):

    def test_loading_sample_data(self):
        self.assertEqual(True, True)


class TestValidRSSCheck(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, 'test_feeds')
        basic_podcast_path = os.path.join(test_feeds_dir, 'itunes_block_podcast.rss')
        basic_podcast_file = open(basic_podcast_path, "rb")
        self.basic_podcast = basic_podcast_file.read()
        self.podcast = Podcast.Podcast(self.basic_podcast)


class TestInvalidRSSCheck(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, 'test_feeds')
        basic_podcast_path = os.path.join(test_feeds_dir, 'missing_info_podcast.rss')
        basic_podcast_file = open(basic_podcast_path, "rb")
        self.basic_podcast = basic_podcast_file.read()
        self.podcast = Podcast.Podcast(self.basic_podcast)


class TestBasicFeedItemBlocked(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, 'test_feeds')
        basic_podcast_path = os.path.join(test_feeds_dir, 'itunes_block_podcast.rss')
        basic_podcast_file = open(basic_podcast_path, "rb")
        self.basic_podcast = basic_podcast_file.read()
        self.podcast = Podcast.Podcast(self.basic_podcast)

    def test_item_itunes_block(self):
        self.assertEqual(self.podcast.itunes_block, True)

    def test_item_itunes_explicit(self):
        self.assertEqual(self.podcast.items[0].itunes_explicit, "yes")
        self.assertEqual(self.podcast.items[1].itunes_explicit, "highly offensive")


class TestBasicFeedItems(unittest.TestCase):

    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, 'test_feeds')
        basic_podcast_path = os.path.join(test_feeds_dir, 'basic_podcast.rss')
        basic_podcast_file = open(basic_podcast_path, "rb")
        self.basic_podcast = basic_podcast_file.read()
        self.podcast = Podcast.Podcast(self.basic_podcast)

    def test_item_count(self):
        number_of_items = len(self.podcast.items)
        self.assertEqual(number_of_items, 2)

    def test_item_description(self):
        self.assertEqual(self.podcast.items[0].description, "basic item description")
        self.assertEqual(self.podcast.items[1].description, "another basic item description")

    def test_item_author(self):
        self.assertEqual(self.podcast.items[0].author, "lawyer@boyer.net")
        self.assertEqual(self.podcast.items[1].author, "lawyer@boyer.net (Lawyer Boyer)")

    def test_item_itunes_author(self):
        self.assertEqual(self.podcast.items[0].itunes_author_name, "basic item itunes author")
        self.assertEqual(self.podcast.items[1].itunes_author_name, "another basic item itunes author")

    def test_item_itunes_block(self):
        self.assertEqual(self.podcast.itunes_block, False)

    def test_item_itunes_duration(self):
        self.assertEqual(self.podcast.items[0].itunes_duration, "1:05")
        self.assertEqual(self.podcast.items[1].itunes_duration, "1:11:05")

    def test_item_itunes_explicit(self):
        self.assertEqual(self.podcast.items[0].itunes_explicit, "no")
        self.assertEqual(self.podcast.items[1].itunes_explicit, "clean")

    def test_item_itunes_order(self):
        self.assertEqual(self.podcast.items[0].itunes_order, "2")
        self.assertEqual(self.podcast.items[1].itunes_order, "1")

    def test_item_itunes_subtitle(self):
        self.assertEqual(self.podcast.items[0].itunes_subtitle, "The Subtitle")
        self.assertEqual(self.podcast.items[1].itunes_subtitle, "Another Subtitle")

    def test_item_itunes_summary(self):
        self.assertEqual(self.podcast.items[0].itunes_summary, "The Summary")
        self.assertEqual(self.podcast.items[1].itunes_summary, "Another Summary")

    def test_item_enclosure_url(self):
        self.assertEqual(self.podcast.items[0].enclosure_url, 'https://github.com/iheartradio/pyPodcastParser.mp3')

    def test_item_enclosure_type(self):
        self.assertEqual(self.podcast.items[0].enclosure_type, 'audio/mpeg')

    def test_item_enclosure_length(self):
        self.assertEqual(self.podcast.items[0].enclosure_length, 123456)

    def test_item_guid(self):
        self.assertEqual(self.podcast.items[0].guid, 'basic item guid')
        self.assertEqual(self.podcast.items[1].guid, 'another basic item guid')

    def test_item_published_date(self):
        self.assertTrue(isinstance(self.podcast.items[1].date_time, datetime.date))

    def test_item_title(self):
        self.assertEqual(self.podcast.items[0].title, "basic item title")
        self.assertEqual(self.podcast.items[1].title, "another basic item title")


class TestBasicFeed(unittest.TestCase):

    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, 'test_feeds')
        basic_podcast_path = os.path.join(test_feeds_dir, 'basic_podcast.rss')
        basic_podcast_file = open(basic_podcast_path, "rb")
        self.basic_podcast = basic_podcast_file.read()
        self.podcast = Podcast.Podcast(self.basic_podcast)

    def test_loding_of_basic_podcast(self):
        self.assertIsNotNone(self.basic_podcast)

    def test_dict(self):
        feed_dict = self.podcast.to_dict()
        self.assertTrue(type(feed_dict) is dict)

    def test_copyright(self):
        self.assertEqual(self.podcast.copyright, "basic copyright")

    def test_description(self):
        self.assertEqual(self.podcast.description, "basic description")

    def test_image(self):
        self.assertEqual(self.podcast.image_url, "https://test/giffy.jpg")

    def test_itunes_author_name(self):
        self.assertEqual(self.podcast.itunes_author_name,
                         "basic itunes author")

    def test_itunes_block(self):
        self.assertEqual(self.podcast.itunes_block, False)

    def test_itunes_categories(self):
        self.assertTrue("News" in self.podcast.itunes_categories)
        self.assertTrue("Business News" in self.podcast.itunes_categories)
        self.assertTrue("Health" in self.podcast.itunes_categories)

    def test_itunes_explicit(self):
        self.assertEqual(self.podcast.itunes_explicit, "clean")

    def test_itunes_complete(self):
        self.assertEqual(self.podcast.itunes_complete, "yes")

    def test_itunes_image(self):
        self.assertEqual(self.podcast.itunes_image,
                         "https://github.com/iheartradio/pyPodcastParser.jpg")

    def test_itunes_categories_length(self):
        number_of_categories = len(self.podcast.itunes_categories)
        self.assertEqual(number_of_categories, 3)

    def test_itunes_keywords(self):
        self.assertTrue("Python" in self.podcast.itunes_keywords)
        self.assertTrue("Testing" in self.podcast.itunes_keywords)

    def test_itunes_keyword_length(self):
        number_of_keywords = len(self.podcast.itunes_keywords)
        self.assertEqual(number_of_keywords, 2)

    def test_itunes_new_feed_url(self):
        self.assertEqual(self.podcast.itunes_new_feed_url, "http://newlocation.com/example.rss")

    def test_language(self):
        self.assertEqual(self.podcast.language, "basic  language")

    def test_last_build_date(self):
        self.assertEqual(self.podcast.last_build_date,
                         "Mon, 24 Mar 2008 23:30:07 GMT")

    def test_link(self):
        self.assertEqual(self.podcast.link,
                         "https://github.com/iheartradio/pyPodcastParser")

    def test_published_date(self):
        self.assertEqual(self.podcast.published_date,
                         "Mon, 24 Mar 2008 23:30:07 GMT")

    def test_owner_name(self):
        self.assertEqual(self.podcast.owner_name, "basic itunes owner name")

    def test_owner_email(self):
        self.assertEqual(self.podcast.owner_email, "basic itunes owner email")

    def test_subtitle(self):
        self.assertEqual(self.podcast.subtitle, "basic itunes subtitle")

    def test_summary(self):
        self.assertEqual(self.podcast.summary, "basic itunes summary")

    def test_summary(self):
        self.assertEqual(self.podcast.summary, "basic itunes summary")

    def test_title(self):
        self.assertEqual(self.podcast.title, "basic title")

    def test_time_published(self):
        self.assertTrue(isinstance(self.podcast.date_time, datetime.date))


class TestUnicodeFeed(unittest.TestCase):

    def setUp(self):
        self.unicodeish_text = u"ℐℑℒℓ℔✕✖✗✘⨒⨓ㄏㄐ㐆㐇㐈㐉蘿螺ﻛﻜﻝﻞ𝀏𝀐𝀑𝀒𝀓ǫǬǭǮǯǰΑΒΓΔΕΖΗΘɥɦɧखगڙښڛ"
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, 'test_feeds')
        basic_podcast_path = os.path.join(test_feeds_dir, 'unicode_podcast.rss')
        basic_podcast_file = open(basic_podcast_path, "rb")
        self.basic_podcast = basic_podcast_file.read()
        self.podcast = Podcast.Podcast(self.basic_podcast)

    def test_loding_of_basic_podcast(self):
        self.assertIsNotNone(self.basic_podcast)

    def test_copyright(self):
        self.assertEqual(self.podcast.copyright, self.unicodeish_text)

    def test_description(self):
        self.assertEqual(self.podcast.description, self.unicodeish_text)

    def test_itunes_author_name(self):
        self.assertEqual(self.podcast.itunes_author_name, self.unicodeish_text)

    def test_itunes_block(self):
        self.assertEqual(self.podcast.itunes_block, False)

    def test_itunes_categories(self):
        self.assertTrue(self.unicodeish_text in self.podcast.itunes_categories)
        self.assertTrue(self.unicodeish_text in self.podcast.itunes_categories)

    def test_itunes_image(self):
        self.assertEqual(self.podcast.itunes_image, self.unicodeish_text)

    def test_itunes_categories_length(self):
        number_of_categories = len(self.podcast.itunes_categories)
        self.assertEqual(number_of_categories, 2)

    def test_itunes_keyword_length(self):
        number_of_keywords = len(self.podcast.itunes_keywords)
        self.assertEqual(number_of_keywords, 2)

    def test_itunes_new_feed_url(self):
        self.assertEqual(self.podcast.itunes_new_feed_url, self.unicodeish_text)

    def test_language(self):
        self.assertEqual(self.podcast.language, self.unicodeish_text)

    def test_last_build_date(self):
        self.assertEqual(self.podcast.last_build_date, self.unicodeish_text)

    def test_link(self):
        self.assertEqual(self.podcast.link, self.unicodeish_text)

    def test_owner_name(self):
        self.assertEqual(self.podcast.owner_name, self.unicodeish_text)

    def test_owner_email(self):
        self.assertEqual(self.podcast.owner_email, self.unicodeish_text)

    def test_subtitle(self):
        self.assertEqual(self.podcast.subtitle, self.unicodeish_text)

    def test_summary(self):
        self.assertEqual(self.podcast.summary, self.unicodeish_text)

    def test_summary(self):
        self.assertEqual(self.podcast.summary, self.unicodeish_text)

    def test_title(self):
        self.assertEqual(self.podcast.title, self.unicodeish_text)


class TestMissingInfoFeed(unittest.TestCase):

    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, 'test_feeds')
        basic_podcast_path = os.path.join(test_feeds_dir, 'missing_info_podcast.rss')
        basic_podcast_file = open(basic_podcast_path, "rb")
        self.basic_podcast = basic_podcast_file.read()
        self.podcast = Podcast.Podcast(self.basic_podcast)

    def test_loding_of_basic_podcast(self):
        self.assertIsNotNone(self.basic_podcast)

    def test_copyright(self):
        self.assertEqual(self.podcast.copyright, None)

    def test_description(self):
        self.assertEqual(self.podcast.description, None)

    def test_image(self):
        self.assertEqual(self.podcast.image_url, None)

    def test_itunes_author_name(self):
        self.assertEqual(self.podcast.itunes_author_name, None)

    def test_itunes_block(self):
        self.assertEqual(self.podcast.itunes_block, False)

    def test_itunes_categories(self):
        self.assertFalse("News" in self.podcast.itunes_categories)
        self.assertFalse("Health" in self.podcast.itunes_categories)

    def test_itunes_explicit(self):
        self.assertEqual(self.podcast.itunes_explicit, None)

    def test_itunes_complete(self):
        self.assertEqual(self.podcast.itunes_complete, None)

    def test_itunes_image(self):
        self.assertEqual(self.podcast.itunes_image, None)

    def test_itunes_categories_length(self):
        number_of_categories = len(self.podcast.itunes_categories)
        self.assertEqual(number_of_categories, 0)

    def test_itunes_keyword_length(self):
        number_of_keywords = len(self.podcast.itunes_keywords)
        self.assertEqual(number_of_keywords, 0)

    def test_itunes_new_feed_url(self):
        self.assertEqual(self.podcast.itunes_new_feed_url, None)

    def test_language(self):
        self.assertEqual(self.podcast.language, None)

    def test_last_build_date(self):
        self.assertEqual(self.podcast.last_build_date, None)

    def test_link(self):
        self.assertEqual(self.podcast.link, None)

    def test_published_date(self):
        self.assertEqual(self.podcast.published_date, None)

    def test_owner_name(self):
        self.assertEqual(self.podcast.owner_name, None)

    def test_owner_email(self):
        self.assertEqual(self.podcast.owner_email, None)

    def test_subtitle(self):
        self.assertEqual(self.podcast.subtitle, None)

    def test_summary(self):
        self.assertEqual(self.podcast.summary, None)

    def test_summary(self):
        self.assertEqual(self.podcast.summary, None)

    def test_title(self):
        self.assertEqual(self.podcast.title, None)

    def test_time_published(self):
        self.assertIsNone(self.podcast.date_time)


class TestItunesBlockFeed(unittest.TestCase):

    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, 'test_feeds')
        basic_podcast_path = os.path.join(
            test_feeds_dir, 'itunes_block_podcast.rss')
        basic_podcast_file = open(basic_podcast_path, "rb")
        self.basic_podcast = basic_podcast_file.read()
        self.podcast = Podcast.Podcast(self.basic_podcast)

    def test_itunes_block(self):
        self.assertEqual(self.podcast.itunes_block, True)

    def test_itunes_explicit(self):
        self.assertEqual(self.podcast.itunes_explicit, "yes")


if __name__ == '__main__':
    unittest.main()
