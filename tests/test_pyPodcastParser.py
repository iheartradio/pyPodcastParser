# -*- coding: utf-8 -*-
import datetime
import os
import unittest
import pytz
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
        test_feeds_dir = os.path.join(test_dir, "test_feeds")
        basic_podcast_path = os.path.join(test_feeds_dir, "itunes_block_podcast.rss")
        basic_podcast_file = open(basic_podcast_path, "rb")
        self.basic_podcast = basic_podcast_file.read()
        self.podcast = Podcast.Podcast(self.basic_podcast)


class TestInvalidRSSCheck(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, "test_feeds")
        basic_podcast_path = os.path.join(test_feeds_dir, "missing_info_podcast.rss")
        basic_podcast_file = open(basic_podcast_path, "rb")
        self.basic_podcast = basic_podcast_file.read()
        self.podcast = Podcast.Podcast(self.basic_podcast)


class TestBasicFeedItemBlocked(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, "test_feeds")
        basic_podcast_path = os.path.join(test_feeds_dir, "itunes_block_podcast.rss")
        basic_podcast_file = open(basic_podcast_path, "rb")
        self.basic_podcast = basic_podcast_file.read()
        self.podcast = Podcast.Podcast(self.basic_podcast)

    def test_item_itunes_block(self):
        self.assertEqual(self.podcast.itunes_block, True)

    def test_item_itunes_explicit(self):
        self.assertEqual(self.podcast.items[0].itunes_explicit, True)
        self.assertEqual(self.podcast.items[1].itunes_explicit, True)


class TestBasicFeedItems(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, "test_feeds")
        basic_podcast_path = os.path.join(test_feeds_dir, "basic_podcast.rss")
        basic_podcast_file = open(basic_podcast_path, "rb")
        self.basic_podcast = basic_podcast_file.read()
        self.podcast = Podcast.Podcast(self.basic_podcast)

    def test_item_count(self):
        number_of_items = len(self.podcast.items)
        self.assertEqual(number_of_items, 2)

    def test_item_description(self):
        self.assertEqual(self.podcast.items[0].description, "basic item description")
        self.assertEqual(
            self.podcast.items[1].description, "another basic item description"
        )

    def test_item_author(self):
        self.assertEqual(self.podcast.items[0].author, "lawyer@boyer.net")
        self.assertEqual(
            self.podcast.items[1].author, "lawyer@boyer.net (Lawyer Boyer)"
        )

    def test_item_itunes_author(self):
        self.assertEqual(
            self.podcast.items[0].itunes_author_name, "basic item itunes author"
        )
        self.assertEqual(
            self.podcast.items[1].itunes_author_name, "another basic item itunes author"
        )

    def test_item_itunes_block(self):
        self.assertEqual(self.podcast.itunes_block, False)

    def test_item_itunes_duration(self):
        self.assertEqual(self.podcast.items[0].itunes_duration, 65)
        self.assertEqual(self.podcast.items[1].itunes_duration, 4265)

    def test_item_itunes_explicit(self):
        self.assertEqual(self.podcast.items[0].itunes_explicit, False)
        self.assertEqual(self.podcast.items[1].itunes_explicit, False)

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
        self.assertEqual(
            self.podcast.items[0].enclosure_url,
            "https://github.com/iheartradio/pyPodcastParser.mp3",
        )

    def test_item_enclosure_type(self):
        self.assertEqual(self.podcast.items[0].enclosure_type, "audio/mpeg")

    def test_item_enclosure_length(self):
        self.assertEqual(self.podcast.items[0].enclosure_length, 123456)

    def test_item_guid(self):
        self.assertEqual(self.podcast.items[0].guid, "basic item guid")
        self.assertEqual(self.podcast.items[1].guid, "another basic item guid")

    def test_item_published_date(self):
        self.assertTrue(isinstance(self.podcast.items[1].date_time, datetime.date))

    def test_item_title(self):
        self.assertEqual(self.podcast.items[0].title, "basic item title")
        self.assertEqual(self.podcast.items[1].title, "another basic item title")


class TestBasicFeed(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, "test_feeds")
        basic_podcast_path = os.path.join(test_feeds_dir, "basic_podcast.rss")
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

    def test_type(self):
        self.assertEqual(self.podcast.itunes_type, "full")

    def test_description(self):
        self.assertEqual(self.podcast.description, "basic description")

    def test_image(self):
        self.assertEqual(self.podcast.image_url, "https://test/giffy.jpg")

    def test_itunes_author_name(self):
        self.assertEqual(self.podcast.itunes_author_name, "basic itunes author")

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
        self.assertEqual(
            self.podcast.itunes_image,
            "https://github.com/iheartradio/pyPodcastParser.jpg",
        )

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
        self.assertEqual(
            self.podcast.itunes_new_feed_url, "http://newlocation.com/example.rss"
        )

    def test_language(self):
        self.assertEqual(self.podcast.language, "basic  language")

    def test_last_build_date(self):
        self.assertEqual(self.podcast.last_build_date, "Mon, 24 Mar 2008 23:30:07 GMT")

    def test_link(self):
        self.assertEqual(
            self.podcast.link, "https://github.com/iheartradio/pyPodcastParser"
        )

    def test_published_date(self):
        self.assertEqual(self.podcast.published_date, "2008-03-24 23:30:07")

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

    def test_interactive(self):
        self.assertFalse(self.podcast.interactive)


class TestIHRInteractiveFeed(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, "test_feeds")
        basic_podcast_path = os.path.join(test_feeds_dir, "ihr_interactive_podcast.rss")
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
        self.assertEqual(self.podcast.itunes_author_name, "basic itunes author")

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
        self.assertEqual(
            self.podcast.itunes_image,
            "https://github.com/iheartradio/pyPodcastParser.jpg",
        )

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
        self.assertEqual(
            self.podcast.itunes_new_feed_url, "http://newlocation.com/example.rss"
        )

    def test_language(self):
        self.assertEqual(self.podcast.language, "basic  language")

    def test_last_build_date(self):
        self.assertEqual(self.podcast.last_build_date, "Mon, 24 Mar 2008 23:30:07 GMT")

    def test_link(self):
        self.assertEqual(
            self.podcast.link, "https://github.com/iheartradio/pyPodcastParser"
        )

    def test_published_date(self):
        self.assertEqual(self.podcast.published_date, "2008-03-24 23:30:07")

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

    def test_interactive(self):
        self.assertTrue(self.podcast.interactive)


class TestKeywordVariability(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, "test_feeds")
        basic_podcast_path = os.path.join(test_feeds_dir, "keyword_variability.rss")
        keyword_variability_file = open(basic_podcast_path, "rb")
        self.podcast = Podcast.Podcast(keyword_variability_file.read())

    def test_keywords(self):
        self.assertEqual(sorted(self.podcast.itunes_keywords), ["Python", "Testing"])


class TestKeywordAbsence(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, "test_feeds")
        basic_podcast_path = os.path.join(test_feeds_dir, "no_keywords.rss")
        no_keywords = open(basic_podcast_path, "rb")
        self.podcast = Podcast.Podcast(no_keywords.read())

    def test_keywords(self):
        self.assertEqual(self.podcast.itunes_keywords, [])


class TestMissingInfoFeed(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, "test_feeds")
        basic_podcast_path = os.path.join(test_feeds_dir, "missing_info_podcast.rss")
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

    def test_interactive(self):
        self.assertFalse(self.podcast.interactive)


class TestItunesBlockFeed(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, "test_feeds")
        basic_podcast_path = os.path.join(test_feeds_dir, "itunes_block_podcast.rss")
        basic_podcast_file = open(basic_podcast_path, "rb")
        self.basic_podcast = basic_podcast_file.read()
        self.podcast = Podcast.Podcast(self.basic_podcast)

    def test_itunes_block(self):
        self.assertEqual(self.podcast.itunes_block, True)

    def test_itunes_explicit(self):
        self.assertEqual(self.podcast.itunes_explicit, "yes")


class TestItunesEpisodes(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, "test_feeds")
        basic_podcast_path = os.path.join(test_feeds_dir, "episode.rss")
        basic_podcast_file = open(basic_podcast_path, "rb")
        self.basic_podcast = basic_podcast_file.read()
        self.podcast = Podcast.Podcast(self.basic_podcast)

    def test_episode_meta_data_episode_type(self):
        self.assertEqual(self.podcast.items[0].itunes_episode_type, "full")

    def test_episode_meta_data_episode_num(self):
        self.assertEqual(self.podcast.items[0].itunes_episode, "111")

    def test_episode_meta_data_episode_season(self):
        self.assertEqual(self.podcast.items[0].itunes_season, "3")

    def test_episode_meta_data_pub_date(self):
        self.assertEqual(self.podcast.items[0].published_date, "2022-05-30 00:05:03")
        self.assertEqual(self.podcast.items[1].published_date, "2022-05-30 07:05:03")
        self.assertEqual(self.podcast.items[2].published_date, "2022-05-30 00:05:03")

        current_time = datetime.datetime.now(pytz.timezone("US/Eastern")).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.assertEqual(self.podcast.items[3].published_date, current_time)
        self.assertEqual(self.podcast.items[4].published_date, "2023-05-22 00:00:00")
        self.assertEqual(
            self.podcast.items[5].published_date, "2023-07-06 04:00:00"
        )  # PDT TO EST

        # TODO: add these back once timezone offset handling is reintroduced.
        # self.assertEqual(self.podcast.items[6].published_date, "2023-12-22 17:00:00")
        # self.assertEqual(self.podcast.items[7].published_date, "2023-12-21 20:00:00")

    def test_episode_meta_data_external_image_url(self):
        self.assertEqual(
            self.podcast.items[0].itunes_image,
            "https://cdn.images.adorilabs.com/v1/df2e8faf-d164-4b52-b101-437415245524.png",
        )

    def test_episode_meta_data_link_title(self):
        self.assertEqual(self.podcast.items[0].itunes_season, "3")

    def test_episode_meta_data_is_interactive(self):
        self.assertEqual(self.podcast.items[0].is_interactive, True)
        self.assertEqual(self.podcast.items[1].is_interactive, True)

    def test_episode_meta_data_interactive(self):
        self.assertEqual(self.podcast.items[0].interactive, True)
        self.assertEqual(self.podcast.items[1].interactive, True)

    def test_episode_meta_data_interactive(self):
        self.assertEqual(self.podcast.items[0].itunes_duration, "2785")
        self.assertEqual(self.podcast.items[1].itunes_duration, "2785")

    def test_episode_meta_data_content_encoded(self):
        self.assertEqual(self.podcast.items[0].content_encoded, "test")
        self.assertEqual(self.podcast.items[1].content_encoded, "test")

    def test_episode_meta_data_description(self):
        self.assertEqual(self.podcast.items[0].description, "description")
        self.assertEqual(self.podcast.items[1].description, "description")

    def test_transcription_is_none(self):
        self.assertEqual(self.podcast.items[0].podcast_transcript, None)


class TestItunesEpisodesParsing(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, "test_feeds")
        basic_podcast_path = os.path.join(test_feeds_dir, "episode_parsing.rss")
        basic_podcast_file = open(basic_podcast_path, "rb")
        self.basic_podcast = basic_podcast_file.read()
        self.podcast = Podcast.Podcast(self.basic_podcast)

    # def test_episode_parsing_meta_data_pub_date(self):
    #     self.assertEqual(
    #         str(self.podcast.items[0].published_date), "2021-07-19 16:14:29"
    #     )

    def test_episode_parsing_meta_data_description(self):
        self.assertEqual(self.podcast.items[0].description, "test")

    def test_episode_meta_data_episode_num(self):
        self.assertEqual(self.podcast.items[0].itunes_episode, "0")

    def test_episode_meta_data_episode_season(self):
        self.assertEqual(self.podcast.items[0].itunes_season, "0")

    def test_episode_parsing_explicit(self):
        self.assertEqual(self.podcast.items[0].itunes_explicit, False)


class TestItunesEpisodeParsingWithTranscription(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, "test_feeds")
        basic_podcast_path = os.path.join(test_feeds_dir, "episode_parsing.rss")
        basic_podcast_file = open(basic_podcast_path, "rb")
        self.basic_podcast = basic_podcast_file.read()
        self.podcast = Podcast.Podcast(self.basic_podcast)

    def test_transcript_is_list_of_dictionaries(self):
        self.assertIsNotNone(self.podcast.items[0].podcast_transcript)

    def test_episode_parsing_transcription_data_episode_transcription(self):
        print(self.podcast.items[0].podcast_transcript)
        self.assertEqual(
            self.podcast.items[0].podcast_transcript[0].get("url"), "episode_1_srt"
        )
        self.assertEqual(
            self.podcast.items[0].podcast_transcript[0].get("type"), "application/srt"
        )
        self.assertEqual(
            self.podcast.items[0].podcast_transcript[0].get("language"), None
        )
        self.assertEqual(self.podcast.items[0].podcast_transcript[0].get("rel"), None)
        self.assertEqual(
            self.podcast.items[0].podcast_transcript[1].get("url"), "episode_1_plain"
        )
        self.assertEqual(
            self.podcast.items[0].podcast_transcript[1].get("type"), "text/plain"
        )
        self.assertEqual(
            self.podcast.items[0].podcast_transcript[1].get("language"), None
        )
        self.assertEqual(
            self.podcast.items[0].podcast_transcript[1].get("rel"), "relation"
        )
        self.assertEqual(
            self.podcast.items[1].podcast_transcript[1].get("url"),
            "episode_2_srt_with_language",
        )
        self.assertEqual(
            self.podcast.items[1].podcast_transcript[1].get("type"), "application/srt"
        )
        self.assertEqual(
            self.podcast.items[1].podcast_transcript[1].get("language"), "US-en"
        )


class TestInvalidPodcastFeed(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, "test_feeds")
        invalid_podcast_path = os.path.join(test_feeds_dir, "invalid_show_dates.rss")
        invalid_podcast_file = open(invalid_podcast_path, "rb")
        self.invalid_podcast = invalid_podcast_file.read()

    def test_invalid_podcast_feed(self):
        with self.assertRaises(Podcast.InvalidPodcastFeed) as context:
            Podcast.Podcast(self.invalid_podcast)
        self.assertTrue(
            'Invalid Podcast Feed, show level pubDate: "2022-2022-2202-020202", could not be parsed'
            == str(context.exception)
        )


class TestInvalidEpisodeDates(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, "test_feeds")
        invalid_episode_path = os.path.join(test_feeds_dir, "invalid_episode_dates.rss")
        with open(invalid_episode_path, "rb") as invalid_episode_file:
            self.invalid_episode = invalid_episode_file.read()

    def test_invalid_episode_dates(self):
        with self.assertRaises(Podcast.InvalidPodcastFeed) as context:
            Podcast.Podcast(self.invalid_episode)
        self.assertTrue(
            'Invalid Podcast Feed, show level pubDate: "Mon, 24 Mar 2008 23:30:07 GMT", could not be parsed'
            == str(context.exception)
        )


class TestAlternateEnclosureFeed(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        test_feeds_dir = os.path.join(test_dir, "test_feeds")
        alt_enclosure_path = os.path.join(test_feeds_dir, "alternate_enclosure.rss")
        alt_enclosure_file = open(alt_enclosure_path, "rb")
        self.alt_enclosure_feed = alt_enclosure_file.read()
        self.podcast = Podcast.Podcast(self.alt_enclosure_feed)

    def test_item_count(self):
        """Test that all three items are parsed"""
        self.assertEqual(len(self.podcast.items), 3)

    def test_first_item_has_alternate_enclosures(self):
        """Test that first item has multiple alternate enclosures"""
        item = self.podcast.items[0]
        self.assertIsNotNone(item.alternate_enclosures)
        self.assertEqual(len(item.alternate_enclosures), 4)

    def test_standard_enclosure_still_works(self):
        """Test that standard enclosure attributes are still parsed"""
        item = self.podcast.items[0]
        self.assertEqual(item.enclosure_url, "https://example.com/episode001.mp3")
        self.assertEqual(item.enclosure_type, "audio/mpeg")
        self.assertEqual(item.enclosure_length, 43200000)

    def test_mp3_alternate_enclosure_attributes(self):
        """Test MP3 alternate enclosure with default=true"""
        item = self.podcast.items[0]
        mp3_enclosure = item.alternate_enclosures[0]
        
        self.assertEqual(mp3_enclosure["mime_type"], "audio/mpeg")
        self.assertEqual(mp3_enclosure["length"], 43200000)
        self.assertEqual(mp3_enclosure["bitrate"], 128000.0)
        self.assertEqual(mp3_enclosure["default"], True)
        self.assertEqual(mp3_enclosure["title"], "Standard MP3")

    def test_mp3_alternate_enclosure_sources(self):
        """Test MP3 alternate enclosure has multiple sources"""
        item = self.podcast.items[0]
        mp3_enclosure = item.alternate_enclosures[0]
        
        self.assertEqual(len(mp3_enclosure["sources"]), 3)
        
        # Check HTTPS source - all sources should have the same integrity
        self.assertEqual(mp3_enclosure["sources"][0]["uri"], "https://example.com/episode001.mp3")
        self.assertIsNone(mp3_enclosure["sources"][0]["content_type"])
        self.assertEqual(mp3_enclosure["sources"][0]["integrity_type"], "sri")
        self.assertEqual(mp3_enclosure["sources"][0]["integrity_value"], "sha384-ExVqijpSE+cRZuKN5LoVBBsPA6dyjmRH5cXjqfiDD8fmtXi3pdb+qOiFvQdkWh1R")
        
        # Check IPFS source - should also have integrity
        self.assertEqual(mp3_enclosure["sources"][1]["uri"], "ipfs://QmdwGqd3d2gFPGeJNLLCshdiPert45fMu84552Y4XHTy4y")
        self.assertEqual(mp3_enclosure["sources"][1]["integrity_type"], "sri")
        self.assertEqual(mp3_enclosure["sources"][1]["integrity_value"], "sha384-ExVqijpSE+cRZuKN5LoVBBsPA6dyjmRH5cXjqfiDD8fmtXi3pdb+qOiFvQdkWh1R")
        
        # Check torrent source - should also have integrity
        self.assertEqual(mp3_enclosure["sources"][2]["uri"], "https://example.com/episode001.torrent")
        self.assertEqual(mp3_enclosure["sources"][2]["content_type"], "application/x-bittorrent")
        self.assertEqual(mp3_enclosure["sources"][2]["integrity_type"], "sri")
        self.assertEqual(mp3_enclosure["sources"][2]["integrity_value"], "sha384-ExVqijpSE+cRZuKN5LoVBBsPA6dyjmRH5cXjqfiDD8fmtXi3pdb+qOiFvQdkWh1R")

    def test_mp3_alternate_enclosure_integrity(self):
        """Test MP3 alternate enclosure has integrity in all sources"""
        item = self.podcast.items[0]
        mp3_enclosure = item.alternate_enclosures[0]
        
        # Check that all sources have the same integrity values
        for source in mp3_enclosure["sources"]:
            self.assertIsNotNone(source["integrity_type"])
            self.assertIsNotNone(source["integrity_value"])
            self.assertEqual(source["integrity_type"], "sri")
            self.assertEqual(source["integrity_value"], "sha384-ExVqijpSE+cRZuKN5LoVBBsPA6dyjmRH5cXjqfiDD8fmtXi3pdb+qOiFvQdkWh1R")

    def test_opus_alternate_enclosure(self):
        """Test Opus alternate enclosure parsing"""
        item = self.podcast.items[0]
        opus_enclosure = item.alternate_enclosures[1]
        
        self.assertEqual(opus_enclosure["mime_type"], "audio/opus")
        self.assertEqual(opus_enclosure["length"], 32400000)
        self.assertEqual(opus_enclosure["bitrate"], 96000.0)
        self.assertEqual(opus_enclosure["title"], "High Quality Opus")
        self.assertEqual(len(opus_enclosure["sources"]), 2)

    def test_video_alternate_enclosure(self):
        """Test video alternate enclosure with height, codecs, and lang"""
        item = self.podcast.items[0]
        video_enclosure = item.alternate_enclosures[2]
        
        self.assertEqual(video_enclosure["mime_type"], "video/mp4")
        self.assertEqual(video_enclosure["length"], 10562995)
        self.assertEqual(video_enclosure["bitrate"], 681483.55)
        self.assertEqual(video_enclosure["height"], 1080)
        self.assertEqual(video_enclosure["codecs"], "avc1.64001f, mp4a.40.2")
        self.assertEqual(video_enclosure["lang"], "en")
        self.assertEqual(len(video_enclosure["sources"]), 3)
        
        # Check Tor source
        self.assertIn("example.onion", video_enclosure["sources"][2]["uri"])

    def test_hls_alternate_enclosure(self):
        """Test HLS streaming alternate enclosure"""
        item = self.podcast.items[0]
        hls_enclosure = item.alternate_enclosures[3]
        
        self.assertEqual(hls_enclosure["mime_type"], "application/x-mpegURL")
        self.assertEqual(hls_enclosure["title"], "HLS Stream")
        self.assertEqual(len(hls_enclosure["sources"]), 1)
        self.assertIn("master.m3u8", hls_enclosure["sources"][0]["uri"])

    def test_second_item_with_rel_attribute(self):
        """Test second item with bonus content (different rel)"""
        item = self.podcast.items[1]
        self.assertEqual(len(item.alternate_enclosures), 2)
        
        # Check main content
        main_enclosure = item.alternate_enclosures[0]
        self.assertEqual(main_enclosure["default"], True)
        self.assertIsNone(main_enclosure["rel"])
        
        # Check bonus content
        bonus_enclosure = item.alternate_enclosures[1]
        self.assertEqual(bonus_enclosure["title"], "Behind the Scenes")
        self.assertEqual(bonus_enclosure["rel"], "bonus")
        self.assertEqual(bonus_enclosure["length"], 12000000)

    def test_third_item_no_alternate_enclosures(self):
        """Test third item has no alternate enclosures"""
        item = self.podcast.items[2]
        self.assertEqual(len(item.alternate_enclosures), 0)
        
        # But standard enclosure should still work
        self.assertEqual(item.enclosure_url, "https://example.com/episode003.mp3")
        self.assertEqual(item.enclosure_length, 28800000)

    def test_to_dict_includes_alternate_enclosures(self):
        """Test that to_dict() includes alternate_enclosures"""
        item = self.podcast.items[0]
        item_dict = item.to_dict()
        
        self.assertIn("alternate_enclosures", item_dict)
        self.assertEqual(len(item_dict["alternate_enclosures"]), 4)

    def test_to_dict_includes_enclosure_object(self):
        """Test that to_dict() includes enclosure object with length and mime_type"""
        item = self.podcast.items[0]
        item_dict = item.to_dict()
        
        self.assertIn("enclosure", item_dict)
        self.assertIsInstance(item_dict["enclosure"], dict)
        self.assertIn("url", item_dict["enclosure"])
        self.assertIn("enclosure_length", item_dict["enclosure"])
        self.assertIn("enclosure_type", item_dict["enclosure"])
        
        # Verify the values match the item attributes
        self.assertEqual(item_dict["enclosure"]["url"], item.enclosure_url)
        self.assertEqual(item_dict["enclosure"]["enclosure_length"], item.enclosure_length)
        self.assertEqual(item_dict["enclosure"]["enclosure_type"], item.enclosure_type)

    def test_optional_attributes_can_be_none(self):
        """Test that optional attributes are None when not present"""
        item = self.podcast.items[0]
        mp3_enclosure = item.alternate_enclosures[0]
        
        # These attributes weren't specified for MP3 enclosure
        self.assertIsNone(mp3_enclosure["height"])
        self.assertIsNone(mp3_enclosure["lang"])
        self.assertIsNone(mp3_enclosure["codecs"])
        self.assertIsNone(mp3_enclosure["rel"])


if __name__ == "__main__":
    unittest.main()
