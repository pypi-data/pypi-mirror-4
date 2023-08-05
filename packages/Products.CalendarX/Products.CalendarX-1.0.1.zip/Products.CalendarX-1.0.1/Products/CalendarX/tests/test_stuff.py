"""All tests, all thrown together, till we notice categories emerge and can split them up"""

from Products.PloneTestCase import PloneTestCase
from Products.Five.testbrowser import Browser


PloneTestCase.installProduct('CalendarX')
PloneTestCase.setupPloneSite(products=['CalendarX'])


class TestStuff(PloneTestCase.PloneTestCase):
    def afterSetUp(self):
        self.loginAsPortalOwner()
        self.portal.invokeFactory('CalendarXFolder', id='calendar')
        self.calendar = self.portal.get('calendar')
    
    def testCreation(self):
        """Make sure the calendar got made."""
        self.failUnless(self.calendar is not None, msg="Failed to make a new CalendarX Folder.")
    
    def testDefaultView(self):
        """Make sure you can view the default view without it exploding."""
        self.failUnless("Number of months to display in the multi-month view" in self.portal['calendar'](), msg="Viewing the calendar didn't work.")

# This doesn't test what it should test:    
#     def testViewAction(self):
#         """Make sure you can view 'calendar/view' without it exploding."""
#         browser = Browser()
#         browser.handleErrors = False
#         page = browser.open(self.calendar.absolute_url() + '/view').read()
#         self.failUnless("Number of months to display in the multi-month view" in page, msg="Known failure: Viewing 'calendar/view' didn't work.")


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestStuff))
    return suite
