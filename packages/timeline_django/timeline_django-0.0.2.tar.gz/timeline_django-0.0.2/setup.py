#!/usr/bin/env python
# Copyright (c) 2012, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 only.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# GNU Lesser General Public License version 3 (see the file LICENSE).

import os

from setuptools import setup, find_packages

setup(
    name='timeline_django',
    version='0.0.2', # Also edit timeline_django/__init__.py when changing.
    packages=find_packages(),
    include_package_data=True,
    maintainer='Launchpad developers',
    maintainer_email='launchpad-dev@lists.launchpad.net',
    description='Insert Django database queries in to a Timeline',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README')).read(),
    license='LGPLv3',
    url='http://launchpad.net/python-timeline-django',
    download_url='https://launchpad.net/python-timeline-django/+download',
    test_suite='timeline_django.tests.test_suite',
    install_requires = [
        'Django',
        ],
    tests_require = [
        'testtools',
        'timeline',
        'oops',
        'oops-timeline',
        ],
    # Auto-conversion to Python 3.
    use_2to3=True,
    )
