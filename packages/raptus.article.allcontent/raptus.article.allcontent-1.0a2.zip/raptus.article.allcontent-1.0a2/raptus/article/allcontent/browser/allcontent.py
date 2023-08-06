from Acquisition import aq_inner
from zope import interface, component

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView
from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize

from raptus.article.core.config import MANAGE_PERMISSION
from raptus.article.core import RaptusArticleMessageFactory as _
from raptus.article.core import interfaces
from raptus.article.nesting.interfaces import IArticles

class IAllcontent(interface.Interface):
    """ Marker interface for the all content viewlet
    """

class Component(object):
    """ Component which lists the articles with all their content
    """
    interface.implements(interfaces.IComponent)
    component.adapts(interfaces.IArticle)
    
    title = _(u'All content')
    description = _(u'List of the contained articles displayed with all their content.')
    image = '++resource++allcontent.gif'
    interface = IAllcontent
    viewlet = 'raptus.article.allcontent'
    
    def __init__(self, context):
        self.context = context

class Viewlet(ViewletBase):
    """ Viewlet listing contained articles displayed with all their content
    """
    index = ViewPageTemplateFile('allcontent.pt')
    component = "allcontent"
    
    def _class(self, brain, i, l, additional=[]):
        cls = additional
        if i == 0:
            cls.append('first')
        if i == l-1:
            cls.append('last')
        if i % 2 == 0:
            cls.append('odd')
        if i % 2 == 1:
            cls.append('even')
        return ' '.join(cls)
    
    @memoize
    def articles(self):
        provider = IArticles(self.context)
        manageable = interfaces.IManageable(self.context)
        mship = getToolByName(self.context, 'portal_membership')
        if mship.checkPermission(MANAGE_PERMISSION, self.context):
            items = provider.getArticles()
        else:
            items = provider.getArticles(component=self.component)
        items = manageable.getList(items, self.component)
        i = 0
        l = len(items)
        for item in items:
            classes = ['article', 'component',]
            styles = item['obj'].Schema().get('styles', None)
            if styles is not None:
                classes.extend(styles.get(item['obj']))
            item.update({'content': component.getMultiAdapter((item['obj'], self.request), name=u'allcontent')(item.has_key('show') and item['show']),
                         'class': self._class(item['brain'], i, l, classes)})
            if item.has_key('show') and item['show']:
                item['class'] += ' hidden'
            i += 1
        return items

class AllcontentView(BrowserView):
    """ Renders the content part of an article
    """
    interface.implements(interfaces.IArticleView)
    template = ViewPageTemplateFile('allcontent_view.pt')
    
    def __call__(self, simple=False):
        self.simple = simple
        return self.template()
