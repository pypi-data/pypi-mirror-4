from Acquisition import aq_chain
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from collective.cart.core.interfaces import ICart
from collective.cart.core.interfaces import ICartArticle
from collective.cart.core.interfaces import ICartContainer
from collective.cart.core.interfaces import ICartContainerAdapter
from collective.cart.core.interfaces import IShoppingSite
from collective.cart.core.interfaces import IShoppingSiteRoot
from five import grok
from zope.component import getMultiAdapter
from zope.interface import Interface


class ShoppingSite(grok.Adapter):
    """Adapter to provide Shopping Site Root."""

    grok.context(Interface)
    grok.provides(IShoppingSite)

    @property
    def shop(self):
        """Returns Shop Site Root object."""
        context = aq_inner(self.context)
        chain = aq_chain(context)
        chain.sort()
        shops = [obj for obj in chain if IShoppingSiteRoot.providedBy(obj)]
        if shops:
            return shops[0]

    @property
    def cart_container(self):
        """Returns Cart Container object of Shop Site Root."""
        if self.shop:
            query = {
                'object_provides': ICartContainer.__identifier__,
                'path': {
                    'query': '/'.join(self.shop.getPhysicalPath()),
                    'depth': 1,
                },
            }
            catalog = getToolByName(self.context, 'portal_catalog')
            brains = catalog(query)
            if brains:
                return brains[0].getObject()

    @property
    def cart(self):
        """Returns current Cart object."""
        return self._member_cart

    @property
    def _member_cart(self):
        """Returns member Cart object."""
        container = self.cart_container
        if container:
            portal_state = getMultiAdapter(
                (self.context, self.context.REQUEST), name=u"plone_portal_state")
            member = portal_state.member()
            query = {
                'path': {
                    'query': '/'.join(container.getPhysicalPath()),
                    'depth': 1,
                },
                'object_provides': ICart.__identifier__,
                'Creator': member.id,
                'review_state': 'created',
            }
            catalog = getToolByName(self.context, 'portal_catalog')
            brains = catalog(query)
            if brains:
                return brains[0].getObject()

    @property
    def cart_articles(self):
        if self.cart:
            query = {
                'path': '/'.join(self.cart.getPhysicalPath()),
                'object_provides': ICartArticle.__identifier__,
            }
            catalog = getToolByName(self.context, 'portal_catalog')
            return catalog(query)

    def get_cart_article(self, cid):
        if self.cart_articles:
            return [article for article in self.cart_articles if article.id == cid][0].getObject()

    def update_next_cart_id(self):
        """Update next cart ID for the cart container."""
        ICartContainerAdapter(self.cart_container).update_next_cart_id()

    def remove_cart_articles(self, ids):
        """Remove articles of ids from current cart.

        :param ids: List of ids or id in string.
        :type ids: list or str
        """
        if self.cart:
            if isinstance(ids, str):
                ids = [ids]
            for oid in ids:
                del self.cart[oid]
