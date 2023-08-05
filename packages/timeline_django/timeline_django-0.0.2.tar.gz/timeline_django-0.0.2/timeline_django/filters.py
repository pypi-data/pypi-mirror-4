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


SESSION_TABLE_NAME = 'django_session'
USER_TABLE_NAME = 'auth_user'


def _filter_table(query, table, reason):
    if table in query:
        return query.split(" ", 1)[0] + " <%s query redacted>" % reason
    return query


def filter_session_info(query):
    return _filter_table(query, SESSION_TABLE_NAME, 'session')


def filter_user_info(query):
    return _filter_table(query, USER_TABLE_NAME, 'user')


def _filter_query(report, filter_fn):
    timeline = report.get('timeline')
    if timeline is None:
        return
    new_timeline = []
    for event in timeline:
        start, end, category, detail = event[:4]
        detail = filter_fn(detail)
        new_timeline.append((start, end, category, detail) + event[4:])
    report['timeline'] = new_timeline


def filter_session_query(report, context):
    """Filter out queries about the session from the timeline."""
    _filter_query(report, filter_session_info)


def filter_user_query(report, context):
    """Filter out queries about the user from the timeline."""
    _filter_query(report, filter_user_info)


def install_hooks(config):
    """Install on_create hooks in the config to sanitise queries.

    This should be called after the `oops_timeline` hooks are instaled.

    :param config: the `oops.Config` to install the hooks in to.
    """
    config.on_create.append(filter_session_query)
    config.on_create.append(filter_user_query)
