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

import threading

from testtools import TestCase
from testtools.matchers import Is

from .. import wsgi


class TestWSGI(TestCase):

    def setUp(self):
        super(TestWSGI, self).setUp()
        self.patch(wsgi, '_thread_local', threading.local())

    def test_get_environ_is_None_first_call(self):
        self.assertEqual(None, wsgi.get_environ())

    def test_wsgi_sets_timeline(self):
        environ = {}
        start_response = lambda status, headers:None
        app = lambda environ, start_response: ["foo"]
        app = wsgi.make_app(app)
        out = app(environ, start_response)
        self.assertEqual(["foo"], out)
        self.assertThat(wsgi.get_environ(), Is(environ))
