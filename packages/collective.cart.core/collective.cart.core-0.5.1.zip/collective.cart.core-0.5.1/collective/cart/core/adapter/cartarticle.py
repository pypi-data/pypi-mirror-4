from Products.CMFCore.utils import getToolByName
from collective.cart.core.interfaces import ICartArticle
from collective.cart.core.interfaces import ICartArticleAdapter
from five import grok


class CartArticleAdapter(grok.Adapter):
    """Adapter to handle CartArticle."""

    grok.context(ICartArticle)
    grok.provides(ICartArticleAdapter)

    @property
    def orig_article(self):
        """Returns riginar Article object."""
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {'UID': self.context.orig_uuid}
        brains = catalog(query)
        if brains:
            return brains[0].getObject()
