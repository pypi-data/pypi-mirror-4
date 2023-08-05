from collective.cart.core.browser.interfaces import ICollectiveCartCoreLayer
from collective.cart.core.interfaces import IArticle
from collective.cart.core.interfaces import IArticleAdapter
from collective.cart.core.interfaces import ICartArticleAdapter
from collective.cart.core.interfaces import IShoppingSite
from collective.cart.core.interfaces import IShoppingSiteRoot
from five import grok
from plone.app.contentlisting.interfaces import IContentListing
from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets.interfaces import IBelowContentTitle
from plone.app.viewletmanager.manager import OrderedViewletManager


grok.templatedir('viewlets')


class AddToCartViewlet(grok.Viewlet):
    """Viewlet to show add to cart form for salable article."""
    grok.context(IArticle)
    grok.layer(ICollectiveCartCoreLayer)
    grok.name('collective.cart.core.add.to.cart')
    grok.require('zope2.View')
    grok.template('add-to-cart')
    grok.view(IViewView)
    grok.viewletmanager(IBelowContentTitle)

    def update(self):
        form = self.request.form
        if form.get('form.addtocart', None) is not None:
            IArticleAdapter(self.context).add_to_cart()
            return self.render()

    def available(self):
        return IArticleAdapter(self.context).addable_to_cart


class CartViewletManager(OrderedViewletManager, grok.ViewletManager):
    """Viewlet manager for cart view."""
    grok.context(IShoppingSiteRoot)
    grok.layer(ICollectiveCartCoreLayer)
    grok.name('collective.cart.core.cartviewletmanager')


class CartArticlesViewlet(grok.Viewlet):
    """Cart Articles Viewlet Class."""
    grok.context(IShoppingSiteRoot)
    grok.layer(ICollectiveCartCoreLayer)
    grok.name('collective.cart.core.cartarticles')
    grok.require('zope2.View')
    grok.template('cart-articles')
    grok.viewletmanager(CartViewletManager)

    def update(self):
        form = self.request.form
        oid = form.get('form.delete.article', None)
        if oid is not None:
            IShoppingSite(self.context).remove_cart_articles(oid)
            if self.view.cart_articles:
                return self.render()
            else:
                return self.request.response.redirect(self.view.url())

    def _items(self, item):
        """Returns dictionary of content listing items.

        :param item: Iterated object of IContentListing.
        :type item: plone.app.contentlisting.catalog.CatalogContentListingObject

        :rtype dict:
        """
        items = {
            'id': item.getId(),
            'title': item.Title(),
            'description': item.Description(),
            'url': None,
        }
        # If the original object still exists.
        obj = item.getObject()
        orig_article = ICartArticleAdapter(obj).orig_article
        if orig_article:
            items['url'] = orig_article.absolute_url()
        return items

    @property
    def articles(self):
        """Returns list of articles to show in cart."""
        results = []
        for item in IContentListing(self.view.cart_articles):
            results.append(self._items(item))
        return results
