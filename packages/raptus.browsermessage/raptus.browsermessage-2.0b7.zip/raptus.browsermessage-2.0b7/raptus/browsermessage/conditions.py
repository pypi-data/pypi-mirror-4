from zope.interface import implements, Interface
from zope.component import adapts
from zope.schema.fieldproperty import FieldProperty

from Products.CMFCore.utils import getToolByName

from raptus.browsermessage.interfaces import IBrowserCondition, IBrowserConditions


class BrowserCondition(object):
    implements(IBrowserCondition)

    platform = FieldProperty(IBrowserCondition['platform'])
    browser = FieldProperty(IBrowserCondition['browser'])
    version_min = FieldProperty(IBrowserCondition['version_min'])
    version_max = FieldProperty(IBrowserCondition['version_max'])

    def __str__(self):
        return '%s;%s;%s;%s' % (','.join(self.platform), self.browser, self.version_min, self.version_max)

    @staticmethod
    def from_str(string):
        try:
            platform, browser, version_min, version_max = string.split(';')
        except:
            return

        condition = BrowserCondition()
        if not platform:
            condition.platform = set([])
        else:
            condition.platform = set(platform.split(','))
        if browser == 'None':
            condition.browser = None
        else:
            condition.browser = browser
        if version_min == 'None':
            condition.version_min = None
        else:
            condition.version_min = int(version_min)
        if version_max == 'None':
            condition.version_max = None
        else:
            condition.version_max = int(version_max)
        return condition


class BrowserConditions(object):
    implements(IBrowserConditions)
    adapts(Interface)

    def __init__(self, context):
        self.context = context
        self.properties = getToolByName(self.context, 'portal_properties').browsermessage_properties
        

    def add(self, condition):
        self.properties._updateProperty('browsers', list(self.properties.getProperty('browsers', [])) + [str(condition),])

    def clear(self):
        self.properties._updateProperty('browsers', [])

    def __iter__(self):
        conditions = self.properties.getProperty('browsers', [])
        for condition in conditions:
            if condition.startswith('is'):
                condition = self._bbb_conversion(condition)
                if condition is not None:
                    yield condition
                continue
            yield BrowserCondition.from_str(condition)

    def _bbb_conversion(self, string):
        string = string[2:].lower()
        condition = None
        for browser in ('ie', 'firefox', 'safari', 'opera', 'chrome',):
            if string.startswith(browser):
                condition = BrowserCondition()
                condition.browser = browser
                string = string[len(browser):]
                break
        if not string or condition is None:
            return condition
        if string.startswith('on'):
            condition.platform = string[2:]
        else:
            try:
                condition.version_min = int(string)
                condition.version_max = int(string)
            except:
                return None
        return condition
