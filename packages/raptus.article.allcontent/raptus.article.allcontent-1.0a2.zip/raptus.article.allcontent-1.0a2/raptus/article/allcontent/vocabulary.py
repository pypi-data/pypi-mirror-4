from zope import interface, component
from zope.schema.interfaces import IVocabularyFactory
from zope.schema import vocabulary

from raptus.article.allcontent.interfaces import IAllcontentStyleProvider

class StylesVocabulary(object):
    """ Archetypes vocabulary for the style selection field
    """
    interface.implements(IVocabularyFactory)
    
    def __call__(self, context):
        providers = component.getAllUtilitiesRegisteredFor(IAllcontentStyleProvider)
        terms = []
        for provider in providers:
            for value, title in provider.classes():
                terms.append(vocabulary.SimpleTerm(value, None, title))
        return vocabulary.SimpleVocabulary(terms)
