# -*- coding: utf-8 -*-
# Copyright (c) 2013 Rodolphe Quiédeville <rodolphe@quiedeville.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup
import os
from tsung2graphite import __version__

VERSION = __version__

setup(
    name="tsung2graphite",
    version=VERSION,
    description="Push tsung log datas to graphite",
    long_description="""tsung2graphite reads tsung log in json format and push them to a graphite server

* Graphite : http://graphite.wikidot.com/
* Tsung : http://tsung.erlang-projects.org/

""",
    scripts=['tsung2graphite.py'],
    author="Rodolphe Quiédeville",
    author_email="rodolphe@quiedeville.org",
    url="https://gitorious.org/tsung2graphite",
    requires=[],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: System :: Monitoring',
        ],
    include_package_data=True,
    )
