from zope.interface import implements
from zope.component import adapts, getUtility
from zope.schema.interfaces import IVocabularyFactory

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField

from Products.Archetypes import atapi

from raptus.article.core.interfaces import IArticle
from raptus.article.core import RaptusArticleMessageFactory as _

class LinesField(ExtensionField, atapi.LinesField):
    """ LinesField
    """

class ArticleExtender(object):
    """ Adds the styles selection field to the article content type
    """
    implements(ISchemaExtender)
    adapts(IArticle)

    fields = [
        LinesField('styles',
            enforceVocabulary = True,
            vocabulary_factory = 'allcontent.styles.vocabulary',
            storage = atapi.AnnotationStorage(),
            schemata = 'settings',
            widget = atapi.MultiSelectionWidget(
                description = _(u'description_allcontent_styles', default=u'Select the styles of the article when displayed in the all content listing.'),
                label= _(u'label_allcontent_styles', default=u'Listing styles'),
                format='checkbox',
            )
        ),
    ]

    def __init__(self, context):
         self.context = context
         
    def getFields(self):
        vocabulary = getUtility(IVocabularyFactory, 'allcontent.styles.vocabulary')(self.context)
        if not len(vocabulary):
            return []
        return self.fields
