#! /usr/bin/env python

from distutils.core import setup


from seth import Daemon


DESCRIPTION = open('README').read()

VERSION=Daemon.version

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Natural Language :: English",
    "Operating System :: POSIX",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",] + [
   ("Programming Language :: Python :: %s" % x) for x in "2.7 3.2 3.3".split()]

LICENSE = """\
Copyright 2007, 2009 Sander Marechal <s.marechal@jejik.com>
Copyright 2010, 2011, 2012 Jack Kaliko <kaliko@azylum.org>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
                                                                     
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
                                                                     
You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.\
"""


setup(
    name="python-seth",
    version=VERSION,
    description="Python Daemon library",
    py_modules=["seth"],
    long_description=DESCRIPTION,
    author="Jack Kaliko",
    author_email="kaliko@azylum.org",
    url="http://git.kaliko.me/?p=python-seth.git;a=summary",
    download_url="http://pypi.python.org/pypi/python-seth/",
    classifiers=CLASSIFIERS,
    license=LICENSE,
    keywords=["daemon", "unix"],
    platforms=["POSIX"]
)


# vim: set expandtab shiftwidth=4 softtabstop=4 textwidth=79:
