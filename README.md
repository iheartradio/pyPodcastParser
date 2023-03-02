
# pyPodcastParser


pypodcastparser is a podcast parser. It should parse any RSS file, but it specializes in parsing podcast rss feeds. pypodcastparser is agnostic about the method you use to get a podcast RSS feed. Most users will be comfortable with the Requests library.


.. _Requests: http://docs.python-requests.org/en/latest/


## Installation
Before you start:

- Services should always be run inside of virtualenvs_.
- Dependencies are managed with pip_ and pip-tools_. Virtualenvs come with
  pip preinstalled; pip-tools should be installed manually with ``python -m pip
  install pip-tools``.
- Make sure you have follow the steps
[here](https://github.com/iheartradio/content-platform-documentation/blob/master/private_python_modules/README.md)
so you can download our private repositories.

Before the first run of the service::

    $ pip install pip-tools
    $ pip install -r requirements-dev.txt
    $ pre-commit install
    $ pip-compile requirements-public.in
    $ pip install -r requirements-public.txt
    $ pip-compile requirements-private.in
    $ pip install -r requirements-private.txt

.. _virtualenvs: https://virtualenv.pypa.io/
.. _pip: https://pip.pypa.io/
.. _pip-tools: https://github.com/nvie/pip-tools/


# Running tests locally

Run test suite:

`tox`

# Deploying a new version

To manually deploy/test a new version:

- Increment the version in setup.py, make sure CodeArtifact doesn't already have a repo for that version

- Make sure `dist` directory is empty, then follow instructions [here](https://github.com/iheartradio/content-platform-documentation/blob/master/private_python_modules/README.md#publishing-with-twine)

If you redeploy a new version of the same version tag, clear pip cache in dependent repos:
`rm -rf ~/Library/Caches/pip/*`


## Service Installation

   $ pip install pypodcastparser


## Usage


   from pypodcastparser.Podcast import Podcast
   import requests

   response = requests.get('https://some_rss_feed')
   podcast = Podcast(response.content)



## Objects and their Useful Attributes


**Notes:**

* All attributes with empty or nonexistent element will have a value of None.
* Attributes are generally strings or lists of strings, because we want to record the literal value of elements.
* The cloud element aka RSS Cloud is not supported as it has been superseded by the superior PubSubHubbub protocal


## Podcast


* categories (list) A list for strings representing the feed categories
* copyright (string): The feed's copyright
* creative_commons (string): The feed's creative commons license
* items (list): A list of Item objects
* description (string): The feed's description
* generator (string): The feed's generator
* image_title (string): Feed image title
* image_url (string): Feed image url
* image_width (string): Feed image width
* image_height (Sample H4string): Feed image height
* itunes_author_name (string): The podcast's author name for iTunes
* itunes_block (boolean): Does the podcast block itunes
* itunes_categories (list): List of strings of itunes categories
* itunes_explicit (string): Is this item explicit. Should only be "yes" and "clean."
* itune_image (string): URL to itunes image
* itunes_keywords (list): List of strings of itunes keywords
* itunes_new_feed_url (string): The new url of this podcast
* itunes_type (string): Episodic for non-chronological episodes, serial for chronological episodes.
* language (string): Language of feed
* last_build_date (string): Last build date of this feed
* link (string): URL to homepage
* managing_editor (string): managing editor of feed
* published_date (string): Date feed was published
* pubsubhubbub (string): The URL of the pubsubhubbub service for this feed
* owner_name (string): Name of feed owner
* owner_email (string): Email of feed owner
* subtitle (string): The feed subtitle
* title (string): The feed title
* ttl (string): The time to live or number of minutes to cache feed
* web_master (string): The feed's webmaster
* date_time (datetime): When published


## Item


* author (string): The author of the item
* comments (string): URL of comments
* creative_commons (string): creative commons license for this item
* description (string): Description of the item.
* enclosure_url (string): URL of enclosure
* enclosure_type (string): File MIME type
* enclosure_length (integer): File size in bytes
* guid (string): globally unique identifier
* itunes_author_name (string): Author name given to iTunes
* itunes_block (boolean): It this Item blocked from itunes
* itunes_closed_captioned: (string): It is this item have closed captions
* itunes_duration (string): Duration of enclosure
* itunes_explicit (string): Is this item explicit. Should only be "yes" and "clean."
* itune_image (string): URL of item cover art
* itunes_order (string): Override published_date order
* itunes_subtitle (string): The item subtitle
* itunes_summary (string): The summary of the item
* link (string): The URL of item.
* published_date (string): Date item was published
* title (string): The title of item.
* date_time (datetime): When published


## Links/Known issues
NA

## Notes
NA
