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
import unittest

def test_suite():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'timeline_django.test_settings'
    module_names = [
        'timeline_django.tests.test_filters',
        'timeline_django.tests.test_hooks',
        'timeline_django.tests.test_wsgi',
        'timeline_django.tests.test_timeline_cursor',
        ]
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromNames(module_names)
    return suite
