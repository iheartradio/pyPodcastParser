from setuptools import setup, find_packages
from codecs import open
from os import path
import os

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()
released_version = "1.9.2dev171"

setup(
    name="pypodcastparser-ihr",
    version=released_version,
    description="pypodcastparser is a podcast parser.",
    long_description=long_description,
    url="https://github.com/iheartradio/pypodcastparser",
    author="Christian Paul, Jason Rigden",
    author_email="christianpaul@iheartmedia.com, jasonrigden@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: XML",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
    ],
    install_requires=[
        "beautifulsoup4",
        "lxml",
    ],
    keywords=["podcast", "parser", "rss", "feed"],
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
)
