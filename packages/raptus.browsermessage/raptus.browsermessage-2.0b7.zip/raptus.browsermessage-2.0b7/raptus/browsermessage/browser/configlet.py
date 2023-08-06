from zope.component import adapts
from zope.formlib import form
from zope.interface import implements
from zope.app.form import CustomWidgetFactory
from zope.app.form.browser.sequencewidget import ListSequenceWidget
from zope.app.form.browser.objectwidget import ObjectWidget

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.controlpanel.form import ControlPanelForm
from plone.app.controlpanel.widgets import MultiCheckBoxVocabularyWidget

from raptus.browsermessage import _
from raptus.browsermessage.conditions import BrowserCondition
from raptus.browsermessage.interfaces import IBrowserConditionsForm, IBrowserConditions


class BrowserMessageControlPanelAdapter(SchemaAdapterBase):
    adapts(IPloneSiteRoot)
    implements(IBrowserConditionsForm)

    def __init__(self, context):
        super(BrowserMessageControlPanelAdapter, self).__init__(context)
        self.browserconditions = IBrowserConditions(self.context)
        self.actions = getToolByName(self.context, 'portal_actions')['browsermessage_actions']

    def get_conditions(self):
        return [condition for condition in self.browserconditions]

    def set_conditions(self, value):
        self.browserconditions.clear()
        for condition in value:
            self.browserconditions.add(condition)

    conditions = property(get_conditions, set_conditions)

    def get_proposals(self):
        proposals = set([])
        for action in self.actions.listActions():
            if action.visible:
                proposals.add(action.id)
        return proposals

    def set_proposals(self, value):
        for action in self.actions.listActions():
            action._updateProperty('visible', action.id in value)

    proposals = property(get_proposals, set_proposals)


class BrowserMessageControlPanel(ControlPanelForm):

    form_fields = form.FormFields(IBrowserConditionsForm)
    form_fields['conditions'].custom_widget = CustomWidgetFactory(ListSequenceWidget, subwidget=CustomWidgetFactory(ObjectWidget, BrowserCondition))
    form_fields['proposals'].custom_widget = MultiCheckBoxVocabularyWidget
    label = _(u'Manage browser message')
    description = u''

