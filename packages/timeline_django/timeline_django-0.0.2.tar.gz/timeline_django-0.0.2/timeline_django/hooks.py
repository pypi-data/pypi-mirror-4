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

from datetime import timedelta
import threading

import django.core.signals
import django.db.backends.signals
import django.db.models.signals


class TimelineReceiver(object):
    """Converts django signals in to `Timeline` entries.

    To use this instantiate on instance, passing a callable that
    will return the timeline, and then call `connect_to_signals`.
    """

    INIT_CATEGORY = "model-init"
    SAVE_CATEGORY = "model-save"
    DELETE_CATEGORY = "model-delete"
    REQUEST_CATEGORY = "request"
    REQUEST_EXCEPTION_CATEGORY = "request-exception"
    CONNECTION_CREATED_CATEGORY = "connection-created"

    def __init__(self, timeline_factory):
        """Create a TimelineReceiver.

        :param timeline_factory: a callable that takes no arguments,
            and returns a `Timeline` object or `None`. This will
            be called each time a `Timeline` is needed in reponse
            to a signal.
        """
        self.timeline_factory = timeline_factory
        self._actions = threading.local()

    def _model_name(self, model_cls):
        return "%s.%s" % (model_cls.__module__, model_cls.__name__)

    def _action_name(self, category, sender):
        return "%s-%s" % (category, self._model_name(sender))

    def _handle_pre(self, category, sender, **kwargs):
        timeline = self.timeline_factory()
        if timeline is None:
            return
        action = timeline.start(category, self._model_name(sender),
                allow_nested=True)
        attr = self._action_name(category, sender)
        actions = getattr(self._actions, attr, [])
        actions.append(action)
        setattr(self._actions, attr, actions)

    def _handle_post(self, category, sender, **kwargs):
        timeline = self.timeline_factory()
        if timeline is None:
            return
        action_name = self._action_name(category, sender)
        actions = getattr(self._actions, action_name, [])
        if not actions:
            raise AssertionError(
                "post action called without pre action. action_name=%r" %
                (action_name,))
        action = actions.pop()
        setattr(self._actions, action_name, actions)
        action.finish()

    def pre_init(self, sender, **kwargs):
        self._handle_pre(self.INIT_CATEGORY, sender, **kwargs)

    def post_init(self, sender, **kwargs):
        self._handle_post(self.INIT_CATEGORY, sender, **kwargs)

    def pre_save(self, sender, **kwargs):
        self._handle_pre(self.SAVE_CATEGORY, sender, **kwargs)

    def post_save(self, sender, **kwargs):
        self._handle_post(self.SAVE_CATEGORY, sender, **kwargs)

    def pre_delete(self, sender, **kwargs):
        self._handle_pre(self.DELETE_CATEGORY, sender, **kwargs)

    def post_delete(self, sender, **kwargs):
        self._handle_post(self.DELETE_CATEGORY, sender, **kwargs)

    # TODO: m2m_changed
    # TODO: 'using' kwarg in to the detail

    def request_started(self, sender, **kwargs):
        self._handle_pre(self.REQUEST_CATEGORY, sender, **kwargs)

    def request_finished(self, sender, **kwargs):
        self._handle_post(self.REQUEST_CATEGORY, sender, **kwargs)

    def _do_instantaneous_action(self, category, detail):
        timeline = self.timeline_factory()
        if timeline is None:
            return
        action = timeline.start(category, detail)
        action.duration = timedelta()

    def got_request_exception(self, sender, **kwargs):
        self._do_instantaneous_action(self.REQUEST_EXCEPTION_CATEGORY,
                self._model_name(sender))

    def connection_created(self, sender, **kwargs):
        connection = kwargs.get('connection', None)
        if connection is not None:
            connection_name = connection.alias
        else:
            connection_name = "(unknown)"
        self._do_instantaneous_action(self.CONNECTION_CREATED_CATEGORY,
                connection_name)

    def connect_to_signals(self):
        """Connect the callbacks to their corresponding signals."""
        django.db.models.signals.pre_init.connect(self.pre_init, weak=False)
        django.db.models.signals.post_init.connect(self.post_init, weak=False)
        django.db.models.signals.pre_save.connect(self.pre_save, weak=False)
        django.db.models.signals.post_save.connect(self.post_save, weak=False)
        django.db.models.signals.pre_delete.connect(self.pre_delete, weak=False)
        django.db.models.signals.post_delete.connect(self.post_delete, weak=False)
        django.core.signals.request_started.connect(self.request_started, weak=False)
        django.core.signals.request_finished.connect(self.request_finished, weak=False)
        django.core.signals.got_request_exception.connect(self.got_request_exception, weak=False)
        django.db.backends.signals.connection_created.connect(self.connection_created, weak=False)
