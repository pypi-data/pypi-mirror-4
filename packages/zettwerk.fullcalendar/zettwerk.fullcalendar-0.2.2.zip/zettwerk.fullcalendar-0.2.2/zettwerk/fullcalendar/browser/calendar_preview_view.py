from zope.interface import implements, Interface

from zope.i18n import translate
from zettwerk.fullcalendar.browser.calendarview import CalendarView


class ICalendarPreviewView(Interface):
    """
    calendar view interface
    """


class CalendarPreviewView(CalendarView):
    """
    calendar browser view that shows the calendar
    """

    implements(ICalendarPreviewView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.preview = translate(u'(Preview)',
                                 domain='zettwerk.fullcalendar',
                                 context=self.request)
