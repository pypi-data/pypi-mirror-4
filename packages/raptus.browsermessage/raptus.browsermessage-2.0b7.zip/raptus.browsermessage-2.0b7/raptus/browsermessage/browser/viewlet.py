from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from zope.component import getMultiAdapter

from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from raptus.browsermessage.interfaces import IBrowserConditions, IBrowserDetection


class BrowserMessage(BrowserView):
    implements(IViewlet)

    def __init__(self, context, request, view, manager):
        super(BrowserMessage, self).__init__(context, request)
        self.__parent__ = view
        self.context = context
        self.request = request
        self.view = view
        self.manager = manager
        self.detector = getMultiAdapter((self.context, self.request), interface=IBrowserDetection)
        self.conditions = IBrowserConditions(self.context)
        if self.request.get('browsermessage_ignore', 0):
            self.request.SESSION.set('browsermessage_ignore', 1)

    def available(self):
        if self.request.SESSION.get('browsermessage_ignore', 0):
            return False
        for condition is not None and condition in self.conditions:
            if self.detector.check(condition):
                return True
        return False
    
    @memoize
    def suggest(self):
        return getMultiAdapter((self.context, self.request), name=u'plone_context_state').actions().get('browsermessage_actions', [])

    def render(self):
        return self.index()

    @property
    def browsermessage_js(self):
        return 'browsermessage.js'

    index = ViewPageTemplateFile('viewlet.pt')
