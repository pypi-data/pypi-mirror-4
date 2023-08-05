from zope.schema.interfaces import IVocabularyFactory
from zope.interface import implements, alsoProvides
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.i18nmessageid import MessageFactory
from zope.i18n import translate

from Acquisition import aq_get

import pdb

from Products.CMFCore.utils import getToolByName
_ = MessageFactory('plone')

# Copied from plone.app.vocabularies-1.0.5-py2.4.egg/plone/app/vocabularies/workflow.py

class PloneboardVocabulary(object):
    """Vocabulary factory PloneboardPortlet."""

    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getattr(context, 'context', context)
        catalog = getToolByName(context, 'portal_catalog', None)
        if catalog is None:
            return None
        # Why is decode necessary here?
        items = [(b.getObject().absolute_url(relative=1) + ' - ' + b.Title.decode('utf-8'), b.UID) for b in catalog(meta_type='Ploneboard')]
        items.sort()
        items = [SimpleTerm(i[1], i[1], i[0]) for i in items]
        return SimpleVocabulary(items)

PloneboardVocabularyFactory = PloneboardVocabulary()
alsoProvides(PloneboardVocabularyFactory, IVocabularyFactory)
