from zope.app.component.hooks import getSite
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

from Products.CMFCore.utils import getToolByName


class SpeakerVocabulary(object):
    """Vocabulary factory returning all available speakers.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        site = getSite()
        catalog = getToolByName(site, 'portal_catalog')
        items = {}
        for speaker in catalog(portal_type='SPSpeaker'):
            items[speaker.getPath()] = SimpleTerm(
                                            speaker.getPath(),
                                            speaker.getPath(),
                                            speaker.Title)

        return SimpleVocabulary(items.values())

SpeakerVocabularyFactory = SpeakerVocabulary()


class CategoriesVocabulary(object):
    """ Vocabulary factory for Categories (Subject)
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        context = getSite()
        catalog = getToolByName(context, 'portal_catalog')
        result = list(catalog.uniqueValuesFor("Subject"))
        result.sort()

        terms = [SimpleTerm(k, title=k) for k in result]

        return SimpleVocabulary(terms)

CategoriesVocabularyFactory = CategoriesVocabulary()
