import unittest
from zettwerk.fullcalendar.tests.base import TestCase

from zope.publisher.browser import TestRequest
from zope.component import getMultiAdapter
from DateTime import DateTime


class TestSetup(TestCase):

    def afterSetUp(self):
        """This method is called before each single test. It can be used to
        set up common state. Setup that is specific to a particular test
        should be done in that test method.
        """
        self.setRoles(['Manager'])

        self.portal.invokeFactory('Event', 'event1')
        self.portal.invokeFactory('Event', 'event2')
        self.portal.invokeFactory('Topic', 'cal')

        self.cal = getattr(self.portal, 'cal')
        self.event1 = getattr(self.portal, 'event1')
        self.event2 = getattr(self.portal, 'event2')
        self.request = TestRequest()
        self.calView = getMultiAdapter((self.cal, self.request),
                                       name='events_view')

        self.cal.setTitle('Kalender Topic')
        self.event1.setTitle('Testevent 1')
        self.event1.setStartDate(DateTime('2010/06/16 07:00:00 GMT+2'))
        self.event1.setEndDate(DateTime('2010/06/17 23:55:00 GMT+2'))
        self.event2.setTitle('Testevent 2')
        self.event2.setStartDate(DateTime('2010/06/17 00:00:00 GMT+2'))
        self.event2.setEndDate(DateTime('2010/06/17 00:00:00 GMT+2'))

        self.portal.portal_catalog.refreshCatalog()

    def beforeTearDown(self):
        """This method is called after each single test. It can be used for
        cleanup, if you need it. Note that the test framework will roll back
        the Zope transaction at the end of each test, so tests are generally
        independent of one another. However, if you are modifying external
        resources (say a database) or globals (such as registering a new
        adapter in the Component Architecture during a test), you may want to
        tear things down here.
        """

    def test_getEvents(self):
        start = '1275256800'
        end = '1278885600'
        result = self.calView.getEvents(start, end)

        self.assertEqual(type(result), type([]))
        self.assertEqual(len(result), 2)

    def test_encodeJSON(self):
        data1 = ['Item1', 'Item2']
        data2 = {'one': 1}
        data3 = 3
        data4 = 'foobar'

        self.assertEqual(self.calView._encodeJSON(data1), '["Item1", "Item2"]')
        self.assertEqual(self.calView._encodeJSON(data2), '{"one": 1}')
        self.assertEqual(self.calView._encodeJSON(data3), '3')
        self.assertEqual(self.calView._encodeJSON(data4), '"foobar"')

    def test_buildDict(self):
        brain1 = self.portal.portal_catalog(UID=self.event1.UID())[0]
        brain2 = self.portal.portal_catalog(UID=self.event2.UID())[0]
        result1 = self.calView._buildDict(brain1)
        result2 = self.calView._buildDict(brain2)

        self.assertEqual(result1['url'], self.event1.absolute_url())
        self.assertEqual(result1['title'], self.event1.Title())
        self.assertEqual(result2['allDay'], True)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSetup))
    return suite
