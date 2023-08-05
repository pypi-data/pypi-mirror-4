from zope.interface import implements, Interface
from zope.i18n import translate

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from simplejson.encoder import JSONEncoder

from zettwerk.fullcalendar import fullcalendarMessageFactory as _


class ICalendarView(Interface):
    """
    calendar view interface
    """

    def getDefaultOptions():
        """ build fullcalendar options dict var defaultCalendarOptions = {} """

    def _encodeJSON(data):
        """ encodes given data in json """

    def _localizedWeekdays():
        """ returns localized weekdays """

    def _localizedWeekdaysShort():
        """ returns localized weekdays short"""

    def _localizedMonthNames():
        """ returns localized month names """

    def _localizedMonthNamesShort():
        """ returns localized month names short"""

    def _localizedNames():
        """ return localized strings """


class CalendarView(BrowserView):
    """
    calendar browser view that shows the calendar
    """

    implements(ICalendarView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.preview = ''

    @property
    def portal_translation(self):
        return getToolByName(self.context, 'translation_service')

    @property
    def site_properties(self):
        return getToolByName(self.context, 'portal_properties').site_properties

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def _localizedWeekdays(self):
        """ returns localized weekdays """
        ret = []
        trans = self.portal_translation.translate
        for i in range(7):
            ret.append(trans(self.portal_translation.day_msgid(i),
                             domain='plonelocales',
                             context=self.context.REQUEST))
        return ret

    def _localizedWeekdaysShort(self):
        """ returns localized weekdays short"""
        ret = []
        trans = self.portal_translation.translate
        for i in range(7):
            ret.append(trans(self.portal_translation.day_msgid(i, 's'),
                             domain='plonelocales',
                             context=self.context.REQUEST))
        return ret

    def _localizedMonthNames(self):
        """ returns localized month names """
        ret = []
        trans = self.portal_translation.translate
        for i in range(1, 13):
            ret.append(trans(self.portal_translation.month_msgid(i),
                             domain='plonelocales',
                             context=self.context.REQUEST))
        return ret

    def _localizedMonthNamesShort(self):
        """ returns localized month names short"""
        ret = []
        trans = self.portal_translation.translate
        for i in range(1, 13):
            ret.append(trans(self.portal_translation.month_msgid(i, 'a'),
                             domain='plonelocales',
                             context=self.context.REQUEST))
        return ret

    def _localizedNames(self):
        """ return localized strings """
        return {'localizedAllDay': translate(_(u'All day'),
                                             context=self.request),
                'localizedToday': translate(_(u'Today'),
                                            context=self.request),
                'localizedDay': translate(_(u'Day'),
                                          context=self.request),
                'localizedWeek': translate(_(u'Week'),
                                           context=self.request),
                'localizedMonth': translate(_(u'Month'),
                                            context=self.request),
               }

    def _encodeJSON(self, data):
        """ takes whats given and jsonfies it """
        return JSONEncoder().encode(data)

    def getDefaultOptions(self):
        """ build fullcalendar options dict var defaultCalendarOptions = {} """
        namesDict = self._localizedNames()

        uiEnabled = False
        try:
            getToolByName(self.context, 'portal_ui_tool')
            uiEnabled = True
        except AttributeError:
            pass

        # Get the localTimeOnlyFormat from the Plone site properties,
        # but default to 24h time if not found
        # Then, convert it to the format that fullcalendar is expecting
        # This strikes me as being hacky, but seems to work well.
        try:
            localTimeOnlyFormat = self.site_properties.localTimeOnlyFormat
        except AttributeError:
            localTimeOnlyFormat = "%H:%M"
        fullCalendarTimeOnlyFormat = localTimeOnlyFormat.replace('%H', 'H') \
            .replace('%M', 'mm') \
            .replace('%I', 'h') \
            .replace('%p', "t.'m'.") \
            .replace('%S', 'ss')

        defaultCalendarOptions = {
            'preview': self.preview,  # this is not a fullcalendar option!
            'theme': uiEnabled,
            'header': {'left': 'prev,next,today',
                       'center': 'title',
                       'right': 'month,agendaWeek,agendaDay'
                       },
            'events': self.context.absolute_url() + '/events_view',
            'allDayText': namesDict['localizedAllDay'],
            'monthNames': self._localizedMonthNames(),
            'monthNamesShort': self._localizedMonthNamesShort(),
            'dayNames': self._localizedWeekdays(),
            'dayNamesShort': self._localizedWeekdaysShort(),
            'titleFormat': {'month': 'MMMM yyyy',
                            'week': "d.[ MMMM][ yyyy]{ - d. MMMM yyyy}",
                            'day': 'dddd, d. MMMM yyyy',
                            },
            'columnFormat': {'month': 'dddd',
                             'week': 'dddd',
                             'day': ''
                             },
            'axisFormat': fullCalendarTimeOnlyFormat,
            'timeFormat':
                {'': fullCalendarTimeOnlyFormat,
                 'agenda': '%s{ - %s}' % (fullCalendarTimeOnlyFormat,
                                          fullCalendarTimeOnlyFormat)},
            'firstDay': 1,
            'buttonText': {'prev': '&nbsp;&#9668;&nbsp;',
                           'next': '&nbsp;&#9658;&nbsp;',
                           'prevYear': '&nbsp;&lt;&lt;&nbsp;',
                           'nextYear': '&nbsp;&gt;&gt;&nbsp;',
                           'today': namesDict['localizedToday'],
                           'month': namesDict['localizedMonth'],
                           'week': namesDict['localizedWeek'],
                           'day': namesDict['localizedDay']
                           },
            }

        return self._encodeJSON(defaultCalendarOptions)
