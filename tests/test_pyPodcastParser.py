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
            "%Y-%m-%d %H:%M"
        )
        self.assertEqual(self.podcast.items[3].published_date, current_time)
        self.assertEqual(self.podcast.items[4].published_date, "2023-05-22 00:00:00")
        self.assertEqual(
            self.podcast.items[5].published_date, "2023-07-06 04:00:00"
        )  # PDT TO EST

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

    def test_episode_parsing_meta_data_pub_date(self):
        self.assertEqual(
            str(self.podcast.items[0].published_date), "2021-07-19 16:14:29"
        )

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


if __name__ == "__main__":
    unittest.main()
