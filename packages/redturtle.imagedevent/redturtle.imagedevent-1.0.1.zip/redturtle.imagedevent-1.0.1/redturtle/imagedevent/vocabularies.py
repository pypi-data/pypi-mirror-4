# -*- coding: utf-8 -*-

from binascii import b2a_qp
from zope.interface import implements

from Products.CMFPlone.utils import safe_unicode
from Products.CMFCore.utils import getToolByName

from zope.schema.interfaces import ISource, IContextSourceBinder, IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary

class EventTypeVocabulary(object):
    """Vocabulary factory listing all catalog keywords from the "getEventType" index
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        self.context = context
        self.catalog = getToolByName(context, "portal_catalog")
        if self.catalog is None:
            return SimpleVocabulary([])
        index = self.catalog._catalog.getIndex('getEventType')

        def safe_encode(term):
            if isinstance(term, unicode):
                # no need to use portal encoding for transitional encoding from
                # unicode to ascii. utf-8 should be fine.
                term = term.encode('utf-8')
            return term

        # Vocabulary term tokens *must* be 7 bit values, titles *must* be
        # unicode
        items = [SimpleTerm(i, b2a_qp(safe_encode(i)), safe_unicode(i))
                 for i in index._index]
        return SimpleVocabulary(items)

EventTypeVocabularyFactory = EventTypeVocabulary()
