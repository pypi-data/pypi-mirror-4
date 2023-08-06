# -*- coding: utf-8 -*-
"""Google Calendar Tool"""

from zope.interface import Interface


class IGoogleCalendarTool(Interface):
    """Google Calendar Tool"""

    def get_events(calendar_id):
        """Returns ordered list of next calendar events."""
        raise NotImplementedError()