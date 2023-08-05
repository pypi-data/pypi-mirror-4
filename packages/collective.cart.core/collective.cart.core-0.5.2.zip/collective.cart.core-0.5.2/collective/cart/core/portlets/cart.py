from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cart.core import _
from collective.cart.core.interfaces import IShoppingSite
from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from zope.interface import implements


class ICartPortlet(IPortletDataProvider):
    '''A portlet which can render cart content.
    '''


class Assignment(base.Assignment):
    implements(ICartPortlet)

    @property
    def title(self):
        """Title shown in @@manage-portlets"""
        return _(u"Cart")


class Renderer(base.Renderer):

    render = ViewPageTemplateFile('cart.pt')

    @property
    def cart_url(self):
        return '{}/@@cart'.format(IShoppingSite(self.context).shop.absolute_url())

    @property
    def available(self):
        if hasattr(self, 'view') and getattr(self.view, 'grokcore.component.directive.name', None) == 'cart':
            return False
        return IShoppingSite(self.context).cart_articles

    @property
    def count(self):
        return len(self.available)


class AddForm(base.NullAddForm):

    def create(self):
        return Assignment()
