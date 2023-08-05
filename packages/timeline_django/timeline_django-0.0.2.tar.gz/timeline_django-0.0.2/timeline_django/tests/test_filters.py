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

import oops
import oops_timeline
from testtools import TestCase
import timeline

from .. import filters


class FilterSessionInfoTests(TestCase):

    def test_leaves_most_queries_be(self):
        query = 'some query'
        result = filters.filter_session_info(query)
        self.assertEqual(query, result)

    def test_redacts_django_session(self):
        query = 'select * from django_session'
        result = filters.filter_session_info(query)
        self.assertEqual('select <session query redacted>', result)


class FilterUserInfoTests(TestCase):

    def test_leaves_most_queries_be(self):
        query = 'some query'
        result = filters.filter_user_info(query)
        self.assertEqual(query, result)

    def test_redacts_django_session(self):
        query = 'select * from auth_user'
        result = filters.filter_user_info(query)
        self.assertEqual('select <user query redacted>', result)


class FilterSessionQueryTests(TestCase):

    def test_does_nothing_no_timeline(self):
        report = {}
        context = {}
        filters.filter_session_query(report, context)
        self.assertEqual({}, report)
        self.assertEqual({}, context)

    def test_filter_session_query(self):
        query = 'select * from django_session'
        test_timeline = [(0, 0, 'some-category', query, 'other')]
        report = dict(timeline=test_timeline)
        filters.filter_session_query(report, {})
        new_timeline = report['timeline']
        self.assertEqual(
                [(0, 0, 'some-category', filters.filter_session_info(query),
                    'other')],
                new_timeline)


class FilterUserQueryTests(TestCase):

    def test_does_nothing_no_timeline(self):
        report = {}
        context = {}
        filters.filter_user_query(report, context)
        self.assertEqual({}, report)
        self.assertEqual({}, context)

    def test_filter_user_query(self):
        query = 'select * from auth_user'
        test_timeline = [(0, 0, 'some-category', query, 'other')]
        report = dict(timeline=test_timeline)
        filters.filter_user_query(report, {})
        new_timeline = report['timeline']
        self.assertEqual(
                [(0, 0, 'some-category', filters.filter_user_info(query),
                    'other')],
                new_timeline)


class FakeConfig(object):

    def __init__(self):
        self.on_create = []


class InstallHooksTests(TestCase):

    def test_installs_filter_session_query(self):
        config = FakeConfig()
        filters.install_hooks(config)
        self.assertIn(filters.filter_session_query, config.on_create)

    def test_installs_filter_user_query(self):
        config = FakeConfig()
        filters.install_hooks(config)
        self.assertIn(filters.filter_user_query, config.on_create)


class IntegrationTests(TestCase):

    def test_publishing_oops_redacts_timeline(self):
        config = oops.Config()
        oops_timeline.install_hooks(config)
        filters.install_hooks(config)
        user_query = 'select * from auth_user'
        session_query = 'select * from django_session'
        test_timeline = timeline.Timeline()
        test_timeline.start('some-category', user_query).finish()
        test_timeline.start('some-other-category', session_query).finish()
        test_context = dict(timeline=test_timeline)
        test_oops = config.create(test_context)
        self.assertEqual(
            [filters.filter_user_info(user_query),
             filters.filter_session_info(session_query),
            ],
            [action[3] for action in test_oops['timeline']])
