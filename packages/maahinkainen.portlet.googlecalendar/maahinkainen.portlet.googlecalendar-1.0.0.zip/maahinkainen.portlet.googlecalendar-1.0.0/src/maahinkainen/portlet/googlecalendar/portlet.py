# -*- coding: utf-8 -*-
"""Google Calendar Portlet"""

from time import time

from Acquisition import aq_inner, aq_parent

from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.component import getUtility

from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.interfaces import ISiteRoot

from plone.portlets.interfaces import IPortletDataProvider

from plone.app.portlets.portlets import base
from plone.app.layout.navigation.defaultpage import isDefaultPage

from plone.memoize import ram

from maahinkainen.portlet.googlecalendar.interfaces import IGoogleCalendarTool

from zope.i18nmessageid import MessageFactory as ZopeMessageFactory
_ = ZopeMessageFactory("maahinkainen.portlet.googlecalendar")

TIMEZONES = SimpleVocabulary([SimpleTerm(ctz, ctz, ctz) for ctz in ["Pacific/Apia", "Pacific/Midway", "Pacific/Niue", "Pacific/Pago_Pago", "Pacific/Fakaofo", "Pacific/Honolulu", "Pacific/Johnston", "Pacific/Rarotonga", "Pacific/Tahiti", "Pacific/Marquesas", "America/Anchorage", "Pacific/Gambier", "America/Los_Angeles", "America/Tijuana", "America/Vancouver", "America/Whitehorse", "Pacific/Pitcairn", "America/Dawson_Creek", "America/Denver", "America/Edmonton", "America/Hermosillo", "America/Mazatlan", "America/Phoenix", "America/Yellowknife", "America/Belize", "America/Chicago", "America/Costa_Rica", "America/El_Salvador", "America/Guatemala", "America/Managua", "America/Mexico_City", "America/Regina", "America/Tegucigalpa", "America/Winnipeg", "Pacific/Easter", "Pacific/Galapagos", "America/Bogota", "America/Cayman", "America/Grand_Turk", "America/Guayaquil", "America/Havana", "America/Iqaluit", "America/Jamaica", "America/Lima", "America/Montreal", "America/Nassau", "America/New_York", "America/Panama", "America/Port-au-Prince", "America/Toronto", "America/Caracas", "America/Anguilla", "America/Antigua", "America/Aruba", "America/Asuncion", "America/Barbados", "America/Boa_Vista", "America/Campo_Grande", "America/Cuiaba", "America/Curacao", "America/Dominica", "America/Grenada", "America/Guadeloupe", "America/Guyana", "America/Halifax", "America/La_Paz", "America/Manaus", "America/Martinique", "America/Montserrat", "America/Port_of_Spain", "America/Porto_Velho", "America/Puerto_Rico", "America/Rio_Branco", "America/Santiago", "America/Santo_Domingo", "America/St_Kitts", "America/St_Lucia", "America/St_Thomas", "America/St_Vincent", "America/Thule", "America/Tortola", "Antarctica/Palmer", "Atlantic/Bermuda", "Atlantic/Stanley", "America/St_Johns", "America/Araguaina", "America/Argentina/Buenos_Aires", "America/Bahia", "America/Belem", "America/Cayenne", "America/Fortaleza", "America/Godthab", "America/Maceio", "America/Miquelon", "America/Montevideo", "America/Paramaribo", "America/Recife", "America/Sao_Paulo", "Antarctica/Rothera", "America/Noronha", "Atlantic/South_Georgia", "America/Scoresbysund", "Atlantic/Azores", "Atlantic/Cape_Verde", "Africa/Abidjan", "Africa/Accra", "Africa/Bamako", "Africa/Banjul", "Africa/Bissau", "Africa/Casablanca", "Africa/Conakry", "Africa/Dakar", "Africa/El_Aaiun", "Africa/Freetown", "Africa/Lome", "Africa/Monrovia", "Africa/Nouakchott", "Africa/Ouagadougou", "Africa/Sao_Tome", "America/Danmarkshavn", "Atlantic/Canary", "Atlantic/Faroe", "Atlantic/Reykjavik", "Atlantic/St_Helena", "Etc/GMT", "Europe/Dublin", "Europe/Lisbon", "Europe/London", "Africa/Algiers", "Africa/Bangui", "Africa/Brazzaville", "Africa/Ceuta", "Africa/Douala", "Africa/Kinshasa", "Africa/Lagos", "Africa/Libreville", "Africa/Luanda", "Africa/Malabo", "Africa/Ndjamena", "Africa/Niamey", "Africa/Porto-Novo", "Africa/Tunis", "Africa/Windhoek", "Europe/Amsterdam", "Europe/Andorra", "Europe/Belgrade", "Europe/Berlin", "Europe/Brussels", "Europe/Budapest", "Europe/Copenhagen", "Europe/Gibraltar", "Europe/Luxembourg", "Europe/Madrid", "Europe/Malta", "Europe/Monaco", "Europe/Oslo", "Europe/Paris", "Europe/Prague", "Europe/Rome", "Europe/Stockholm", "Europe/Tirane", "Europe/Vaduz", "Europe/Vienna", "Europe/Warsaw", "Europe/Zurich", "Africa/Blantyre", "Africa/Bujumbura", "Africa/Cairo", "Africa/Gaborone", "Africa/Harare", "Africa/Johannesburg", "Africa/Kigali", "Africa/Lubumbashi", "Africa/Lusaka", "Africa/Maputo", "Africa/Maseru", "Africa/Mbabane", "Africa/Tripoli", "Asia/Amman", "Asia/Beirut", "Asia/Damascus", "Asia/Gaza", "Asia/Jerusalem", "Asia/Nicosia", "Europe/Athens", "Europe/Bucharest", "Europe/Chisinau", "Europe/Helsinki", "Europe/Istanbul", "Europe/Kaliningrad", "Europe/Kiev", "Europe/Minsk", "Europe/Riga", "Europe/Sofia", "Europe/Tallinn", "Europe/Vilnius", "Africa/Addis_Ababa", "Africa/Asmara", "Africa/Dar_es_Salaam", "Africa/Djibouti", "Africa/Kampala", "Africa/Khartoum", "Africa/Mogadishu", "Africa/Nairobi", "Antarctica/Syowa", "Asia/Aden", "Asia/Baghdad", "Asia/Bahrain", "Asia/Kuwait", "Asia/Qatar", "Asia/Riyadh", "Europe/Moscow", "Europe/Samara", "Indian/Antananarivo", "Indian/Comoro", "Indian/Mayotte", "Asia/Tehran", "Asia/Baku", "Asia/Dubai", "Asia/Muscat", "Asia/Tbilisi", "Asia/Yerevan", "Indian/Mahe", "Indian/Mauritius", "Indian/Reunion", "Asia/Kabul", "Antarctica/Mawson", "Asia/Aqtau", "Asia/Aqtobe", "Asia/Ashgabat", "Asia/Dushanbe", "Asia/Karachi", "Asia/Tashkent", "Asia/Yekaterinburg", "Indian/Kerguelen", "Indian/Maldives", "Asia/Calcutta", "Asia/Colombo", "Asia/Katmandu", "Antarctica/Vostok", "Asia/Almaty", "Asia/Bishkek", "Asia/Dhaka", "Asia/Omsk", "Asia/Thimphu", "Indian/Chagos", "Asia/Rangoon", "Indian/Cocos", "Antarctica/Davis", "Asia/Bangkok", "Asia/Hovd", "Asia/Jakarta", "Asia/Krasnoyarsk", "Asia/Phnom_Penh", "Asia/Saigon", "Asia/Vientiane", "Indian/Christmas", "Antarctica/Casey", "Asia/Brunei", "Asia/Choibalsan", "Asia/Hong_Kong", "Asia/Irkutsk", "Asia/Kuala_Lumpur", "Asia/Macau", "Asia/Makassar", "Asia/Manila", "Asia/Shanghai", "Asia/Singapore", "Asia/Taipei", "Asia/Ulaanbaatar", "Australia/Perth", "Asia/Dili", "Asia/Jayapura", "Asia/Pyongyang", "Asia/Seoul", "Asia/Tokyo", "Asia/Yakutsk", "Pacific/Palau", "Australia/Adelaide", "Australia/Darwin", "Antarctica/DumontDUrville", "Asia/Vladivostok", "Australia/Brisbane", "Australia/Hobart", "Australia/Sydney", "Pacific/Guam", "Pacific/Port_Moresby", "Pacific/Saipan", "Pacific/Truk", "Asia/Kamchatka", "Asia/Magadan", "Pacific/Efate", "Pacific/Guadalcanal", "Pacific/Kosrae", "Pacific/Noumea", "Pacific/Ponape", "Pacific/Norfolk", "Pacific/Auckland", "Pacific/Fiji", "Pacific/Funafuti", "Pacific/Kwajalein", "Pacific/Majuro", "Pacific/Nauru", "Pacific/Tarawa", "Pacific/Wake", "Pacific/Wallis", "Pacific/Enderbury", "Pacific/Tongatapu", "Pacific/Kiritimati"]])


class IGoogleCalendarPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    calendar_title = schema.TextLine(
        title=_(u"Custom Title"),
        description=_(u"Enter a custom title for your upcoming events listing."),
        default=u"",
        required=False)

    calendar_id = schema.ASCIILine(
        title=_(u"Google Calendar ID"),
        description=_(u"Enter the unique id of your published Google Calendar here (e.g. nefpna8dutjcqf4ji58svcerfg@group.calendar.google.com)."),
        default="",
        required=True)

    timezone = schema.Choice(
        title=_(u"Timezone"),
        description=_(u"Select a Google Calendar timezone for embedded month and event listing views."),
        vocabulary=TIMEZONES,
        default='Europe/Helsinki',
        required=True
        )

    event_limit = schema.Int(
        title=_(u"Event Limit"),
        description=_(u"Enter a number, how many upcoming events should be shown at maximum."),
        default=0,
        required=True)

    filter_string = schema.TextLine(
       title=_(u"Filter text"),
       description=_(u"Enter a string, which should be found on every shown event title or description."),
       default=u"",
       required=False)

    siteroot_only = schema.Bool(
       title=_(u"Only on Frontpage"),
       description=_(u"Select this to show this portlet only when on the site root. Otherwise this portlet will be shown normally."),
       default=False,
       required=False)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IGoogleCalendarPortlet)

    @property
    def title(self):
        return self.data.calendar_title or _(u"Google Calendar")

    description = _(u"A portlet showing the next events on a Google Calendar.")

    def __init__(self, calendar_title="", calendar_id="",
                 timezone="Europe/Helsinki", event_limit=0,
                 filter_string=u"", siteroot_only=False):
        super(Assignment, self).__init__()
        self.calendar_title = calendar_title
        self.calendar_id = calendar_id
        self.timezone = timezone or "Europe/Helsinki"
        self.event_limit = event_limit or 0
        self.filter_string = filter_string or u""
        self.siteroot_only = siteroot_only or False


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    render = ViewPageTemplateFile('events.pt')

    @property
    @ram.cache(lambda m, self: (time() // 3600,
        self.data.filter_string, self.data.calendar_id))  # cache for an hour
    def published_events(self):
        calendar = getUtility(IGoogleCalendarTool)(self.data.calendar_id)
        s = self.data.filter_string and self.data.filter_string.lower() or False
        if s and calendar.events:
            return [e for e in calendar.events if\
              unicode(e.get_title(), 'utf-8').lower().find(s) > -1\
              or unicode(e.get_description(), 'utf-8').lower().find(s) > -1]
        else:
            return calendar.events

    @property
    def available(self):
        return self.data.siteroot_only is False and True\
          or ISiteRoot.providedBy(self.context)\
          or ISiteRoot.providedBy(aq_parent(aq_inner(self.context)))\
              and isDefaultPage(aq_parent(aq_inner(self.context)), self.context) \
          or False


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IGoogleCalendarPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IGoogleCalendarPortlet)