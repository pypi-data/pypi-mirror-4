from zope import schema
from zope.interface import implementer
try:
    from zope.site.hooks import getSite
except ImportError: # Plone < 4
    from zope.app.component.hooks import getSite

from Products.CMFCore.utils import getToolByName

@implementer(schema.interfaces.IVocabularyFactory)
def proposals_vocabulary_factory(context):
    try:
        actions = getToolByName(context, 'portal_actions')['browsermessage_actions']
    except:
        actions = getToolByName(getSite(), 'portal_actions')['browsermessage_actions']
    terms = []
    for action in actions.listActions():
        terms.append(schema.vocabulary.SimpleTerm(action.id, action.id, action.title))
    return schema.vocabulary.SimpleVocabulary(terms)
