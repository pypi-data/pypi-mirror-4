#!/usr/bin/env python
import os
import sys

from setuptools import find_packages
from setuptools import setup

from shrink import __version__
from shrink import read_file


CURRENT_DIR = os.path.dirname(__file__)
README = read_file(CURRENT_DIR, "README.rst")
CHANGELOG = read_file(CURRENT_DIR, "CHANGELOG.rst")
DESCRIPTION = "Command line tool for minification of css and javascript files"
LONG_DESCRIPTION = README + "\n\n" + CHANGELOG
AUTHORS = (
    ("Jer\xf3nimo Jos\xe9 Albi", "albi@wienfluss.net"),
)


# special setup parameters
kwargs = {}
if sys.version_info >= (3, 0):
    kwargs['use_2to3'] = True

setup(
    name="shrink",
    version=__version__,
    author=", ".join([a[0] for a in AUTHORS]),
    author_email=", ".join([a[1] for a in AUTHORS]),
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url="https://bitbucket.org/jeronimoalbi/shrink",
    keywords="minify javascript css yuicompressor",
    license="BSD License",
    platforms=["OS Independent"],
    zip_safe=False,
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    tests_require=["nose"],
    test_suite="nose.collector",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Topic :: Utilities",
    ],
    entry_points={
        'console_scripts': [
            "shrink = shrink.command:run",
        ],
    },
    **kwargs
)
