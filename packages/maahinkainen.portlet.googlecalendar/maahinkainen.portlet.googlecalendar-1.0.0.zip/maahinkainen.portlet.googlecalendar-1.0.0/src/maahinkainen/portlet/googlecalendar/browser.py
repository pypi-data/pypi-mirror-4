# -*- coding: utf-8 -*-
"""Traversable Google Calendar Event View"""

import re

from Acquisition import aq_parent

from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse, NotFound

from Products.Five.browser import BrowserView

from maahinkainen.portlet.googlecalendar.utility import EVENTS

LINK_REGEXP = re.compile((r"(\b(http|https)://"
                          r"([-A-Za-z0-9+&@#/%?=~_()|!:,.;]*"
                          r"[-A-Za-z0-9+&@#/%=~_()|]))"))


class Month(BrowserView):
    """View a month, via ../context/@@calendar-month/calendar-id
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        if isinstance(context, Month) or isinstance(context, Event):
            context = aq_parent(context)
        super(Month, self).__init__(context, request)
        self.calendar_id = None
        self.timezone = self.request.get("ctz", "Europe/Helsinki")

        # Disable portlets on ajax_load
        if "ajax_load" in self.request:
            self.request["disable_plone.leftcolumn"] = True
            self.request["disable_plone.rightcolumn"] = True

    def publishTraverse(self, request, name):
        if not self.calendar_id and name in EVENTS:  # ../@@calendar-month/calendar_id
            self.calendar_id = name
        else:
            raise NotFound(self, name, request)
        return self


class Event(BrowserView):
    """View an event, via ../context/@@calendar-event/calendar-id/event-id
    """

    implements(IPublishTraverse)

    def __init__(self, context, request):
        if isinstance(context, Month) or isinstance(context, Event):
            context = aq_parent(context)
        super(Event, self).__init__(context, request)
        self.calendar = {}
        self.timezone = self.request.get("ctz", "Europe/Helsinki")
        self.event = None

        # Disable portlets on ajax_load
        if "ajax_load" in self.request:
            self.request["disable_plone.leftcolumn"] = True
            self.request["disable_plone.rightcolumn"] = True

    def get_title(self):
        return unicode(self.event.get_title(), "utf-8")

    def get_description(self):
        s = unicode(self.event.get_description(), "utf-8")
        for match in LINK_REGEXP.findall(s):
            s = s.replace(match[0], u'<a href="%s">%s</a>' % (match[0], match[0]))
        return s

    def publishTraverse(self, request, name):
        if not self.calendar:  # ../@@calendar-event/calendar_id
            for event in EVENTS.get(name, []):
                self.calendar[event.get_id()] = event
            if not self.calendar:
                raise NotFound(self, name, request)
        elif not self.event:  # ../@@calendar-event/calendar_id/event_id
            self.event = self.calendar.get(name, None)
            if not self.event:
                raise NotFound(self, name, request)
        else:
            raise NotFound(self, name, request)
        return self
