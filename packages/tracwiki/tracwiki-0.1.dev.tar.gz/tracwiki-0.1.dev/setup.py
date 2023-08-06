import sys
from setuptools import setup

if sys.version_info < (2, 6):
    raise Exception("tracwiki requires Python 2.6 or higher.")

# Todo: How does this play with pip freeze requirement files?
requires = ["keyring"]

# Python 2.6 does not include the argparse module.
try:
    import argparse
except ImportError:
    requires.append("argparse")

import tracwiki as distmeta

setup(
    name="tracwiki",
    version=distmeta.__version__,
    description="Checkout and commit trac wiki pages.",
    long_description=distmeta.__doc__,
    author=distmeta.__author__,
    author_email=distmeta.__contact__,
    url=distmeta.__homepage__,
    license="MIT License",
    platforms=["any"],
    packages=["tracwiki"],
    requires=requires,
    install_requires=requires,
    entry_points = {
        "console_scripts": [
            "tracwiki = tracwiki.tracwiki:main",
        ]
    },
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    keywords="trac wiki checkout commit"
)
