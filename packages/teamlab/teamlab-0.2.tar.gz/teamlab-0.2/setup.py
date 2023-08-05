#!/usr/bin/env python
# vim: set fileencoding=utf-8:

from setuptools import setup


DESCRIPTION = """TeamLab is an open source collaboration platform, which has a
built in task manager among other things.  This module implements parts of the
official API, enough for reading the tasks.

The official API documentation is at:

http://api.teamlab.com/
"""

setup(
    author = 'Justin Forest',
    author_email = 'hex@umonkey.net',
    classifiers = [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python :: 2",
        "Topic :: Software Development :: Bug Tracking",
    ],
    description = 'Python interface to TeamLab API',
    license = 'GNU GPL',
    long_description = DESCRIPTION,
    name = 'teamlab',
    packages = ['teamlab'],
    requires = ['json'],
    url = 'http://code.umonkey.net/python-teamlab/',
    version = '0.2'
)
