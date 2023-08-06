# -*- coding: utf-8 -*-
"""Google Calendar Tool"""

from time import time
from datetime import datetime

from zope.interface import implements

from plone.memoize import ram

from gdata.calendar import service
from googlecalendar import CalendarEvent

from maahinkainen.portlet.googlecalendar.interfaces import IGoogleCalendarTool

EVENTS = {}


class GoogleCalendarTool(object):
    implements(IGoogleCalendarTool)

    def __init__(self, calendar_id):
        self.calendar_id = calendar_id

    @property
    @ram.cache(lambda m, self: (time() // 3600, self.calendar_id))  # cache for an hour
    def events(self):
        cs = service.CalendarService()
        params = ("?orderby=starttime"
                  "&sortorder=ascending"
                  "&singleevents=true"
                  "&start-min=%s" % datetime.now().strftime("%Y-%m-%d"))
        uri = "/calendar/feeds/%s/public/full%s" % (self.calendar_id, params)
        feed = cs.GetCalendarEventFeed(uri)
        events = [CalendarEvent(e) for e in feed.entry]
        if events:
            # FIXME: This is not a nice way to save viewable
            # events, but it's better than nothing...
            EVENTS[self.calendar_id] = events
        return events
