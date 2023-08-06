import sys
from setuptools import setup

if sys.version_info < (2, 6):
    raise Exception("mailFilter requires Python 2.6 or higher.")

# Todo: How does this play with pip freeze requirement files?
requires = ["Levenshtein", "email"]

# Python 2.6 does not include the argparse module.
try:
    import argparse
except ImportError:
    requires.append("argparse")

import mailfilter as distmeta

setup(
    name="mailfilter",
    version=distmeta.__version__,
    description="Filter HTML and blacklisted attachments.",
    long_description=distmeta.__doc__,
    author=distmeta.__author__,
    author_email=distmeta.__contact__,
    url=distmeta.__homepage__,
    license="MIT License",
    platforms=["any"],
    packages=["mailfilter"],
    requires=requires,
    install_requires=requires,
    entry_points = {
        "console_scripts": [
            "mailFilter = mailfilter.mailFilter:main",
        ]
    },
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    keywords="mail html blacklist filter"
)
