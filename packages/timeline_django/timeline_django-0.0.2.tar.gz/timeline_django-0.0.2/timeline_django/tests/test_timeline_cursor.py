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

import django.db
import django.core.signals
from django.dispatch import Signal
from testtools import TestCase
from testtools.matchers import StartsWith, EndsWith
from timeline import Timeline

from ..timeline_cursor import (
    TimelineCursor,
    TimelineCursorInserter,
    )


class TestCursor(object):

    def __init__(self):
        self.calls = []
        self.many_calls = []

    def execute(self, sql, params):
        self.calls.append((sql, params))

    def executemany(self, sql, param_list):
        self.many_calls.append((sql, param_list))


class ExpectedException(Exception):
    pass


class RaisingCursor(TestCursor):

    def execute(self, sql, params=None):
        super(RaisingCursor, self).execute(sql, params=params)
        raise ExpectedException()


class ManyRaisingCursor(TestCursor):

    def executemany(self, sql, param_list):
        super(ManyRaisingCursor, self).executemany(sql, param_list)
        raise ExpectedException()


class TestDbOps(object):

    def __init__(self, db):
        self.db = db

    def last_executed_query(self, cursor, sql, params):
        if cursor != self.db.cursor:
            raise AssertionError("Called with wrong cursor: %s" % cursor)
        if len(cursor.calls) < 1:
            raise AssertionError("Called before execute")
        if sql != cursor.calls[-1][0]:
            raise AssertionError("Called with wrong sql: %s" % sql)
        if params != cursor.calls[-1][1]:
            raise AssertionError("Called with wrong params: %s" % params)
        return self.db.last_query


class TestDatabase(object):

    def __init__(self, alias, cursor, last_query):
        self.alias = alias
        self.cursor = cursor
        self.last_query = last_query
        self.ops = TestDbOps(self)


class TimelineCursorTests(TestCase):

    _not_passed = object()

    def get_cursor(self, inner_cursor=None, db=None, alias=None,
            timeline_factory=None, prefix=_not_passed):
        if inner_cursor is None:
            inner_cursor = TestCursor()
        if alias is None:
            alias = self.getUniqueString()
        if db is None:
            db = TestDatabase(alias, inner_cursor, self.getUniqueString())
        if timeline_factory is None:
            timeline = Timeline()
            timeline_factory = lambda: timeline
        if prefix is self._not_passed:
            prefix = self.getUniqueString()
        return TimelineCursor(inner_cursor, db, timeline_factory,
                prefix=prefix)

    def test_execute_with_no_timeline(self):
        inner_cursor = TestCursor()
        cursor = self.get_cursor(inner_cursor=inner_cursor,
                timeline_factory=lambda: None)
        sql = 'SELECT * from foo;'
        params = (self.getUniqueString(),)
        # Shouldn't crash trying to use the None returned from the
        # timeline_factory
        cursor.execute(sql, params)
        self.assertEqual([(sql, params)], inner_cursor.calls)

    def test_execute_creates_action(self):
        timeline = Timeline()
        cursor = self.get_cursor(timeline_factory=lambda: timeline)
        cursor.execute(self.getUniqueString())
        self.assertEqual(1, len(timeline.actions))

    def test_execute_finishes_action(self):
        timeline = Timeline()
        cursor = self.get_cursor(timeline_factory=lambda: timeline)
        cursor.execute(self.getUniqueString())
        self.assertEqual(1, len(timeline.actions))
        # Duration == None indicates that the action is unfinished
        self.assertNotEqual(None, timeline.actions[0].duration)

    def test_execute_calls_cursor(self):
        inner_cursor = TestCursor()
        cursor = self.get_cursor(inner_cursor=inner_cursor)
        sql = 'SELECT * from foo;'
        params=(1, 2,)
        cursor.execute(sql, params=params)
        self.assertEqual(1, len(inner_cursor.calls))
        self.assertEqual((sql, params), inner_cursor.calls[0])

    def test_execute_finishes_action_even_if_inner_cursor_raises(self):
        inner_cursor = RaisingCursor()
        timeline = Timeline()
        cursor = self.get_cursor(inner_cursor=inner_cursor,
                timeline_factory=lambda: timeline)
        self.assertRaises(ExpectedException,
                cursor.execute, self.getUniqueString())
        self.assertEqual(1, len(timeline.actions))
        # Duration == None indicates that the action is unfinished
        self.assertNotEqual(None, timeline.actions[0].duration)

    def test_execute_updates_detail_based_on_last_executed_query(self):
        timeline = Timeline()
        alias = self.getUniqueString()
        inner_cursor = TestCursor()
        last_query = self.getUniqueString()
        db = TestDatabase(alias, inner_cursor, last_query)
        cursor = self.get_cursor(inner_cursor=inner_cursor, db=db,
                timeline_factory=lambda: timeline)
        cursor.execute(self.getUniqueString())
        self.assertEqual(1, len(timeline.actions))
        self.assertEqual(last_query, timeline.actions[0].detail)

    def test_execute_action_starts_with_prefix(self):
        prefix = self.getUniqueString()
        timeline = Timeline()
        cursor = self.get_cursor(timeline_factory=lambda: timeline,
                prefix=prefix)
        cursor.execute(self.getUniqueString())
        self.assertThat(timeline.actions[0].category, StartsWith(prefix))

    def test_execute_default_prefix(self):
        timeline = Timeline()
        cursor = self.get_cursor(timeline_factory=lambda: timeline, prefix=None)
        cursor.execute(self.getUniqueString())
        self.assertThat(timeline.actions[0].category, StartsWith('SQL-'))

    def test_execute_action_ends_with_connection_name(self):
        connection_name = self.getUniqueString()
        timeline = Timeline()
        cursor = self.get_cursor(alias=connection_name,
                timeline_factory=lambda: timeline)
        cursor.execute(self.getUniqueString())
        self.assertThat(timeline.actions[0].category, EndsWith(connection_name))

    def test_executemany_with_no_timeline(self):
        inner_cursor = TestCursor()
        cursor = self.get_cursor(inner_cursor=inner_cursor,
                timeline_factory=lambda: None)
        sql = 'SELECT * from foo;'
        param_list = [(self.getUniqueString(),)]
        # Shouldn't crash trying to use the None returned from the
        # timeline_factory
        cursor.executemany(sql, param_list)
        self.assertEqual([(sql, param_list)], inner_cursor.many_calls)

    def test_executemany_creates_action(self):
        timeline = Timeline()
        cursor = self.get_cursor(timeline_factory=lambda: timeline)
        cursor.executemany(self.getUniqueString())
        self.assertEqual(1, len(timeline.actions))

    def test_executemany_finishes_action(self):
        timeline = Timeline()
        cursor = self.get_cursor(timeline_factory=lambda: timeline)
        cursor.executemany(self.getUniqueString())
        self.assertEqual(1, len(timeline.actions))
        # Duration == None indicates that the action is unfinished
        self.assertNotEqual(None, timeline.actions[0].duration)

    def test_executemany_calls_cursor(self):
        inner_cursor = TestCursor()
        cursor = self.get_cursor(inner_cursor=inner_cursor)
        sql = 'SELECT * from foo;'
        param_list=[(1, 2,)]
        cursor.executemany(sql, param_list)
        self.assertEqual([(sql, param_list)], inner_cursor.many_calls)

    def test_executemany_finishes_action_even_if_inner_cursor_raises(self):
        inner_cursor = ManyRaisingCursor()
        timeline = Timeline()
        cursor = self.get_cursor(inner_cursor=inner_cursor,
                timeline_factory=lambda: timeline)
        self.assertRaises(ExpectedException,
                cursor.executemany, self.getUniqueString())
        self.assertEqual(1, len(timeline.actions))
        # Duration == None indicates that the action is unfinished
        self.assertNotEqual(None, timeline.actions[0].duration)

    def test_executemany_updates_detail_based_on_sql_and_param_list(self):
        timeline = Timeline()
        cursor = self.get_cursor(timeline_factory=lambda: timeline)
        sql = self.getUniqueString()
        param_list = [(self.getUniqueString(),), (self.getUniqueString(),)]
        cursor.executemany(sql, param_list)
        self.assertEqual(1, len(timeline.actions))
        self.assertEqual(sql + " " + str(param_list) , timeline.actions[0].detail)

    def test_executemany_action_starts_with_prefix(self):
        prefix = self.getUniqueString()
        timeline = Timeline()
        cursor = self.get_cursor(timeline_factory=lambda: timeline,
                prefix=prefix)
        cursor.executemany(self.getUniqueString())
        self.assertThat(timeline.actions[0].category, StartsWith(prefix))

    def test_executemany_default_prefix(self):
        timeline = Timeline()
        cursor = self.get_cursor(timeline_factory=lambda: timeline, prefix=None)
        cursor.executemany(self.getUniqueString())
        self.assertThat(timeline.actions[0].category, StartsWith('SQL-'))

    def test_executemany_action_ends_with_connection_name(self):
        connection_name = self.getUniqueString()
        timeline = Timeline()
        cursor = self.get_cursor(alias=connection_name,
                timeline_factory=lambda: timeline)
        cursor.executemany(self.getUniqueString())
        self.assertThat(timeline.actions[0].category, EndsWith(connection_name))


class TestConnection(object):

    def __init__(self, cursor=None):
        self.alias = "an-alias"
        self.cursor = lambda: cursor


class InsertTimelineCursorsTests(TestCase):

    def make_and_patch_connection(self, cursor=None, connection_name=None):
        """Patch the django.db.connections dict with a test double.

        In order to isolate the tests from the environment we
        monkey patch django.db.connections.

        This dict is the mapping from connection name to
        connection (`DatabaseWrapper`.)

        :param cursor: the cursor to use in the mock Connection.
        :param connection_name: the name the connection should have,
            or None for the method to generate an arbitrary unique
            name.
        """
        connection = TestConnection(cursor=cursor)
        if connection_name is None:
            connection_name = self.getUniqueString()
        connections = {connection_name: connection}
        self.patch(django.db, 'connections', connections)
        return connection

    def get_cursor(self):
        return django.db.connections.values()[0].cursor()

    def test_wraps_one_connection(self):
        self.make_and_patch_connection()
        inserter = TimelineCursorInserter(lambda: None)
        inserter.insert_timeline_cursors()
        self.assertEqual(1, len(django.db.connections))
        self.assertIsInstance(self.get_cursor(), TimelineCursor)

    def test_wraps_two_conections(self):
        connections = [TestConnection(), TestConnection()]
        connections = dict(foo=connections[0], bar=connections[1])
        self.patch(django.db, 'connections', connections)
        inserter = TimelineCursorInserter(lambda: None)
        inserter.insert_timeline_cursors()
        self.assertEqual(2, len(connections))
        self.assertIsInstance(connections.values()[0].cursor(), TimelineCursor)
        self.assertIsInstance(connections.values()[1].cursor(), TimelineCursor)

    def test_wraps_original_cursor(self):
        cursor = TestCursor()
        self.make_and_patch_connection(cursor=cursor)
        inserter = TimelineCursorInserter(lambda: None)
        inserter.insert_timeline_cursors()
        self.assertEqual(1, len(django.db.connections))
        self.assertEqual(cursor, self.get_cursor().cursor)

    def test_sets_db(self):
        connection = self.make_and_patch_connection()
        inserter = TimelineCursorInserter(lambda: None)
        inserter.insert_timeline_cursors()
        self.assertEqual(1, len(django.db.connections))
        self.assertEqual(connection, self.get_cursor().db)

    def test_sets_timeline_factory(self):
        self.make_and_patch_connection()
        timeline_factory = lambda: None
        inserter = TimelineCursorInserter(timeline_factory)
        inserter.insert_timeline_cursors()
        self.assertEqual(1, len(django.db.connections))
        self.assertEqual(timeline_factory, self.get_cursor().timeline_factory)

    def test_sets_prefix(self):
        self.make_and_patch_connection()
        prefix = self.getUniqueString()
        inserter = TimelineCursorInserter(lambda: None, prefix=prefix)
        inserter.insert_timeline_cursors()
        self.assertEqual(1, len(django.db.connections))
        self.assertEqual(prefix, self.get_cursor().prefix)

    def test_wraps_only_once(self):
        # Calling twice from same thread doesn't lead to double wrapping
        cursor = TestCursor()
        self.make_and_patch_connection(cursor=cursor)
        inserter = TimelineCursorInserter(lambda: None)
        inserter.insert_timeline_cursors()
        inserter.insert_timeline_cursors()
        self.assertEqual(1, len(django.db.connections))
        # Check that the original connection is now the cursor
        # attribute of the wrapped cursor. If calling
        # insert_timeline_cursors twice wrapped twice then the
        # attribute would be another cursor wrapper that wraps
        # the original cursor.
        self.assertEqual(cursor, self.get_cursor().cursor)

    def patch_signal(self, module, signal_name):
        signal = Signal()
        self.patch(module, signal_name, signal)
        return signal

    def test_register_signals_registers_request_started(self):
        signal = self.patch_signal(django.core.signals, 'request_started')
        inserter = TimelineCursorInserter(lambda: None)
        inserter.connect_to_request_signals()
        self.assertEqual(1, len(signal.receivers))
        self.assertEqual(inserter._request_cb, signal.receivers[0][1])

    def test_request_cb_wraps_one_connection(self):
        self.make_and_patch_connection()
        inserter = TimelineCursorInserter(lambda: None)
        inserter._request_cb(self, something=self.getUniqueString())
        self.assertEqual(1, len(django.db.connections))
        self.assertIsInstance(self.get_cursor(), TimelineCursor)
