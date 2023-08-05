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

"""Thunk layer to expose WSGI variables to Django global hooks."""

import threading


_thread_local = threading.local()


def get_environ():
    """Get the WSGI environ associated with the current request, if any.

    If a WSGI environ has been saved, calling this function will return it
    within the same thread until a new WSGI environ is saved. If none has
    been saved, None is returned.
    """
    return getattr(_thread_local, 'environ', None)


def make_app(application):
    """Create a WSGI application that stores the environ in a thread-local.

    This is useful when dealing with non-WSGI code or code that runs in 
    global contexts such as ORMs, and you wish to work with something in the
    WSGI environ.

    The module function get_environ() will return the saved WSGI environ.

    :return: A WSGI app wrapping application.
    """
    def save_environ(environ, start_response):
        _thread_local.environ = environ
        return application(environ, start_response)
    return save_environ
