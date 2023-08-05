from collective.hootsuite.interfaces import IHootsuiteRegistry
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory


class HootsuiteIds(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        try:
            registry = getUtility(IRegistry)
            settings = registry.forInterface(IHootsuiteRegistry)
            terms = []
            for service in settings.possible_services:
                terms.append(SimpleVocabulary.createTerm(service, service))
            return SimpleVocabulary(terms)
        except:
            return SimpleVocabulary([])

HootsuiteIdsFactory = HootsuiteIds()
