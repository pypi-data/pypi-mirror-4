import re

from zope.interface import implements, Interface
from zope.component import adapts
from zope.publisher.interfaces.http import IHTTPRequest

from raptus.browsermessage.interfaces import IBrowserDetection, UNKNOWN

class BrowserDetection(object):
    implements(IBrowserDetection)
    adapts(Interface, IHTTPRequest)

    _platform = None
    _browser = None
    _version = None

    _version_re = {
        'firefox': re.compile('firefox/([0-9]+)'),
        'safari': re.compile('version/([0-9]+)'),
        'chrome': re.compile('chrome/([0-9]+)'),
        'ie': re.compile('msie ([0-9]+)'),
        'opera': re.compile('version/([0-9]+)')
    }

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self._ua_id = self.request.get('HTTP_USER_AGENT',
                                        u'Detection not supported')
        self._ua = self._ua_id.lower()

    def platform(self):
        if self._platform is not None:
            return self._platform
        if (self._ua.find('windows') > 0) or (self._ua.find('win32') > 0):
            self._platform = 'windows'
        elif (self._ua.find('macintosh') > 0) or (self._ua.find('mac os x') > 0):
            self._platform = 'mac'
        elif self._ua.find('linux') > 0:
            self._platform = 'linux'
        else:
            self._platform = UNKNOWN
        return self._platform

    def browser(self):
        if self._browser is not None:
            return self._browser
        if self._ua.find('opera') >= 0:
            self._browser = 'opera'
        elif self._ua.find('chrome') >= 0:
            self._browser = 'chrome'
        elif self._ua.find('firefox/') > 0:
            self._browser = 'firefox'
        elif self._ua.find('msie') >= 0:
            self._browser = 'ie'
        elif self._ua.find('safari') >= 0:
            self._browser = 'safari'
        else:
            self._browser = UNKNOWN
        return self._browser

    def version(self):
        if self._version is not None:
            return self._version
        if self.browser() is UNKNOWN:
            self._version = UNKNOWN
        else:
            match = self._version_re[self.browser()].search(self._ua)
            if match is None:
                self._version = UNKNOWN
            else:
                self._version = int(match.group(1))
        return self._version

    def check(self, condition):
        if condition.platform is not None and len(condition.platform) and not self.platform() in condition.platform:
            return False
        if condition.browser is not None and not condition.browser == self.browser():
            return False
        if condition.version_min is not None and condition.version_min > self.version():
            return False
        if condition.version_max is not None and condition.version_max < self.version():
            return False
        return True
