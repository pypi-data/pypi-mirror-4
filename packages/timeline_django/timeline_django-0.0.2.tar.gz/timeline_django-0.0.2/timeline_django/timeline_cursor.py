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

from django import db
from django.db.backends.util import CursorWrapper


class TimelineCursor(CursorWrapper):
    """A wrapper around a Django db cursor that records actions in a `Timeline`.

    Wrapping a Django db cursor with a `TimelineCursor` allows for all the
    executed queries to be recorded in a timeline.
    """

    def __init__(self, cursor, db, timeline_factory, prefix=None):
        """Create a `TimelineCursor`.

        :param cursor: the cursor being wrapped.
        :param db: the `DatabaseWrapper` that the cursor is from.
        :param timeline_factory: a callable that takes no arguments
            and returns a `Timeline` instance or None. This will be
            called whenever a new query is made to get the timeline
            to record the action on. If it returns None the action
            won't be recorded.
        :param prefix: the prefix to use for actions inserted in to
            the timeline. If None the default of 'SQL-' will be used.
        """
        super(TimelineCursor, self).__init__(cursor, db)
        self.cursor = cursor
        self.db = db
        self.connection_name = self.db.alias
        self.timeline_factory = timeline_factory
        self.prefix = prefix
        if self.prefix is None:
            self.prefix = 'SQL-'

    def execute(self, sql, params=()):
        action = None
        timeline = self.timeline_factory()
        if timeline is not None:
            action = timeline.start(self.prefix+self.connection_name,
                    sql + " " + str(params))
        try:
            self.cursor.execute(sql, params)
        finally:
            if timeline is not None:
                action.detail = self.db.ops.last_executed_query(self.cursor,
                        sql, params)
                action.finish()

    def executemany(self, sql, param_list=[]):
        action = None
        timeline = self.timeline_factory()
        if timeline is not None:
            action = timeline.start(self.prefix+self.connection_name,
                    sql + " " + str(param_list))
        try:
            self.cursor.executemany(sql, param_list)
        finally:
            if timeline is not None:
                action.finish()


class TimelineCursorInserter(object):
    """Inserts `TimelineCursor`s once per-thread.

    Calling `insert_timeline_cursors` will insert a `TimelineCursor` in to the
    Django db machinery, but skip if this instance has already done that before
    in this thread.

    You can trigger that method such that it will run at least once in each
    thread to ensure that all cursors are wrapped in a `TimelineCursor`.

    A common way to do this is to do it at the start of every request. To
    aid with doing that you can call `connect_to_request_signals` which
    well setup a receiver for `django.core.signals.request_started` to
    call `insert_timeline_cursors`.
    """

    def __init__(self, timeline_factory, prefix=None):
        """Make a `TimelineCursorInserter`.

        :param timeline_factory: a callable that takes no arguments
            and returns a `Timeline` instance or None.
        :param prefix: the prefix to use for the entries recorded
            in the `Timeline`, or None to use the default.
        """
        self._cursor_wrapped = threading.local()
        self.timeline_factory = timeline_factory
        self.prefix = prefix

    def insert_timeline_cursors(self):
        """Insert `TimelineCursor`s in to the db machinery.

        No action will be taken if the method has already been called
        in the current thread.
        """
        if not getattr(self._cursor_wrapped, 'done', False):
            for connection_name in db.connections:
                connection = db.connections[connection_name]
                connection.cursor = self._make_timeline_cursor_wrapper(
                        connection)
            setattr(self._cursor_wrapped, 'done', True)

    def _make_timeline_cursor_wrapper(self, connection):
        _orig_cursor_fn = connection.cursor
        def make_timeline_cursor():
            cursor = _orig_cursor_fn()
            return TimelineCursor(cursor, connection, self.timeline_factory,
                    prefix=self.prefix)
        return make_timeline_cursor

    def _request_cb(self, sender, **kwargs):
        self.insert_timeline_cursors()

    def connect_to_request_signals(self):
        """Connect to the `request_started` signal to insert the cursors.

        After calling this every time the `request_started` signal is
        triggered `insert_timeline_cursors` will be called.
        """
        from django.core.signals import request_started
        request_started.connect(self._request_cb, weak=False)


def setup_timeline_cursor_hooks(timeline_factory, prefix=None):
    """Setup the hooks necessary to insert `TimelineCursor`s.

    Sets up hooks so that at the start of every request a check
    is made that the current thread has a `TimelineCursor` inserted
    in to the db machinery, and insert one if not.

    :param timeline_factory: a callable that takes no arguments
        and returns either a `Timeline` instance, or None.
    :param prefix: the prefix to use for the entries recorded
        in the `Timeline`, or None to use the default.
    """
    inserter = TimelineCursorInserter(timeline_factory, prefix=prefix)
    inserter.connect_to_request_signals()
