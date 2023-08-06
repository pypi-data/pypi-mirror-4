"""Copyright (c) 2009, Sergio Gabriel Teves
All rights reserved.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

"""GoogleCalendar Helper

    Version:    0.1 03-20-2009
                Sergio Gabriel Teves 
                Initial Release
                0.2 03-25-2009
                Process recurrent events
                #TODO: add reminders to recurrent events
                0.3 03-26-2009
                Add reminders limits
                Add recurrence on copy method
"""

import time
import datetime
import copy

import gdata.calendar

import atom

from xml.utils import iso8601

from icalendar import Calendar as iCal, LocalTimezone


class CalendarEvent:
    """CalendarEvent
    
    This class is an event wrapper.
    It allow the user to add and modify events without
    having to worry about atom formats.
    
    """
    SMS = 'sms'
    EMAIL = 'email'
    POPUP = 'alert'
    DEFAULT = 'all'
    MINUTES = 'minutes'
    HOURS = 'hours'
    DAYS = 'days'
    WEEKS = 'weeks'
    
    _DAY = 'DAILY'
    _WEEK = 'WEEKLY'
    _MONTH = 'MONTHLY'
    _YEAR = 'YEARLY'
    
    _event = None    
    _rec = 0
    
    _MAX_REMINDER = 40320 # 4 WEEKS
    _MIN_REMINDER = 5
    
    def __init__(self, event=None, title=None, start_date=None, end_date=None, description=None, where=None):
        """Return an Event Instance
        
        If event is specified all other arguments are ignored
        
        """
        if event is not None:
            self._event = event
            if len(self._event.when)>0:
                self._event.when.sort(key=lambda obj: obj.start_time)
        else:
            self._event = gdata.calendar.CalendarEventEntry()
            if title is not None:
                self.set_title(title)
            if start_date is not None:
                self.set_start_date(start_date)
            if end_date is not None:
                self.set_end_date(end_date)
            if description is not None:
                self.set_description(description)
            if where is not None:
                self.set_where(where)
    
    def __cmp__(self, other):
        return cmp(self.get_start_date(),other.get_start_date())
            
    def __str__(self):
        return ("{id: '%s', title: '%s', start: '%s', end: '%s', description: '%s', where: '%s'}" %
                 (self.get_id(), self.get_title(),self.get_start_date(),
                  self.get_end_date(), self.get_description(), self.get_where()))
                                                                                 
    def _encode_date(self, date):
        if date.__class__ is datetime.date:
            _date = time.strftime('%Y-%m-%d', time.gmtime(time.mktime(date.timetuple())))
        else:
            _date = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime(time.mktime(date.timetuple())))
        return _date
    
    def _decode_date(self, str):
        if len(str) == 10:
            _date = time.strptime(str, '%Y-%m-%d')
            _date = datetime.datetime(_date.tm_year, _date.tm_mon, _date.tm_mday,0,0,0)
        else:
            _date = datetime.datetime.fromtimestamp(iso8601.parse(str))
            _date = _date.replace(tzinfo=None)
        return _date
        
    def set_title(self, title):
        self._event.title = atom.Title(text=title) 
    
    def set_start_date(self, date):
        """pass datetime.date for an all day event, no end date is necessary"""
        _date = self._encode_date(date)

        if len(self._event.when) == 0:
            self._event.when.append(gdata.calendar.When(start_time=_date))
        else:
            self._event.when[0].start_time = _date
    
    def set_end_date(self, date):
        _date = self._encode_date(date)
        if len(self._event.when) == 0:
            self._event.when.append(gdata.calendar.When(end_time=_date))
        else:
            self._event.when[0].end_time = _date
    
    def set_description(self, description):
        self._event.content = atom.Content(text=description)
    
    def set_where(self, where):
        if len(self._event.where) == 0:
            self._event.where.append(gdata.calendar.Where(value_string=where))
        else:
            self._event.where[0] = gdata.calendar.Where(value_string=where)

    def get_title(self):
        return self._event.title.text
    
    def get_start_date(self):
        """return None if no date is set"""
        _date = None
        if len(self._event.when) > 0:
            _date = self._decode_date(self._event.when[self._rec].start_time)
        return _date
    
    def get_end_date(self):
        """return None if no date is set"""
        _date = None
        if len(self._event.when) > 0:
            _date = self._decode_date(self._event.when[self._rec].end_time) 
        return _date

    def _process_recurrence(self):
        return iCal.from_string("BEGIN:VEVENT\n%sEND:VEVENT" % self._event.recurrence.text)
        
    def get_description(self):
        _str=""
        if self._event.content.text is not None:
            _str=self._event.content.text
        return _str
    
    def get_where(self):
        _str = ""
        if len(self._event.where) > 0:
            if self._event.where[0].value_string is not None:
                _str = self._event.where[0].value_string
        return _str

    def get_event(self):
        """return a gdata.calendar.CalendarEventEntry""" 
        return self._event
    
    def add_reminder(self, method="all", minutes=None, hours=None, days=None, weeks=None):
        """
        time_type could be 'minutes','hours', 'days', 'weeks'
        
        """
        if method != "all":
            if weeks is not None:
                minutes = ((weeks * 7) * 24) * 60
            elif days is not None:
                minutes = (days * 24) * 60
            elif hours is not None:
                minutes = hours * 60            
            if minutes > self._MAX_REMINDER:
                minutes = self._MAX_REMINDER
            elif minutes < self._MIN_REMINDER:
                minutes = self._MIN_REMINDER
            _reminder = gdata.calendar.Reminder(minutes=minutes)
        else:
            _reminder = gdata.calendar.Reminder()
            
        _reminder._attributes['method'] = 'method'
        _reminder.method = method
            
        if len(self._event.when) == 0:
            self._event.when.append(gdata.calendar.When())
            self._event.when[0].reminder.append(_reminder)
        else:
            self._event.when[0].reminder.append(_reminder)
        
    def get_reminders(self):
        """Return a read only list of dict in the form {method, type, time}"""
        reminders = []
        if len(self._event.when)>0:
            for a_reminder in self._event.when[0].reminder:
                _reminder = {}
                _reminder["method"] = a_reminder._ToElementTree().get("method")
                _val = int(a_reminder.minutes)
                if _val % 10080 == 0:
                    _reminder["type"] = "weeks"
                    _reminder["time"] = _val / 10080 
                elif _val % 1440 == 0:
                    _reminder["type"] = "days"
                    _reminder["time"] = _val / 1440 
                elif _val % 60 == 0:
                    _reminder["type"] = "hours"
                    _reminder["time"] = _val / 60 
                else:
                    _reminder["type"] = "minutes"
                    _reminder["time"] = _val                    
                reminders.append(_reminder)
        return reminders
    
    def get_id(self):
        _id = None
        if self._event.id is not None:
            _id = self._event.id.text.split("/")[-1].split("_")[0]
        return _id
    
    def copy(self, event):
        self.set_title(event.get_title())
        self.set_description(event.get_description())
        self.set_where(event.get_where())
        self._event.when = event.get_event().when
        self._event.recurrence = event.get_event().recurrence
        #self._event.who = event.who
        
    def get_guests(self): 
        """Returns a list of dict in the form {email, name, type, status}"""
        list = []
        for p, _who in enumerate(self._event.who):
            _guest = {}
            _guest["email"] = _who.email
            _guest["name"] = _who.name
            _guest["type"] = _who.value
            if _who.attendee_status is not None:
                _guest["status"] = _who.attendee_status.value
            else:
                _guest["status"] = "ACCEPTED"
            list.append(_guest)
        return list
    
    def add_guest(self, name, email):
        self._event.who.append(gdata.calendar.Who(name=name, email=email))
    
    def remove_guest(self, email):
        _guest = None
        for p, _who in enumerate(self._event.who):
            if email == _who.email:
                _guest = _who
                break
        if _guest is not None:
            self._event.who.remove(_guest)
    
    def is_recurrent(self):
        return len(self._event.when) > 1
     
    def get_recurrences(self):
        list = []
        for i, a_when in enumerate(self._event.when):
            _new = copy.copy(self)
            _new._rec = i 
            list.append(_new)
        return list
    
    def get_recurrence_data(self):
        r = {}
        c = iCal.from_string("BEGIN:EVENT\n%sEND:EVENT" % self._event.recurrence.text)
        r['DTSTART']=c['DTSTART'].dt
        r['DTEND']=c['DTEND'].dt
        r['FREQ']=c['RRULE']['FREQ'][0]
        if c['RRULE'].has_key('WKST'):
            r['WKST']=c['RRULE']['WKST'][0]
        if c['RRULE'].has_key('UNTIL'):
            r['UNTIL']=c['RRULE']['UNTIL'][0].astimezone(LocalTimezone())
        if c['RRULE'].has_key('BYDAY'):
            r['BYDAY']=c['RRULE']['BYDAY']
        if c['RRULE'].has_key('INTERVAL'):
            r['INTERVAL']=c['RRULE']['INTERVAL'][0]
        return r
    
    def set_recurrence_data(self, freq=None, by_day=None, interval=None, until=None):
        rec = ('DTSTART;TZID=UTC:' + time.strftime('%Y%m%dT%H%M%SZ', self.get_start_date().timetuple()) + '\r\n'
               + 'DTEND;TZID=UTC:' + time.strftime('%Y%m%dT%H%M%SZ', self.get_end_date().timetuple()) + '\r\n'
               + 'RRULE:FREQ=' + freq)
        
        if by_day is not None and len(by_day)>0:
            if by_day.__class__ is list:
                rec += ';BYDAY=' + ",".join(by_day)
            else:
                rec += ';BYDAY=' + by_day
        if interval is not None:
            rec += ';INTERVAL=' + str(int(interval))
        if until is not None:
            _d = self.get_end_date()
            _until = datetime.datetime(until.year, until.month, until.day, _d.hour, _d.minute, 0)
            rec += ';UNTIL=' + time.strftime('%Y%m%dT%H%M%SZ', _until.timetuple())
        rec += "\r\n"

        self._event.recurrence = gdata.calendar.Recurrence(text=rec)