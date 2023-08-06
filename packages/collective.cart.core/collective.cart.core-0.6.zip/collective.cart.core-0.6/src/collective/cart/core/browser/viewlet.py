from collective.cart.core.browser.interfaces import ICollectiveCartCoreLayer
# from collective.cart.core.browser.base import BaseListingObject
from collective.cart.core.interfaces import IArticle
from collective.cart.core.interfaces import IArticleAdapter
from collective.cart.core.interfaces import ICart
# from collective.cart.core.interfaces import IShoppingSite
from collective.cart.core.interfaces import IShoppingSiteRoot
from five import grok
from plone.app.layout.globals.interfaces import IViewView
from plone.app.layout.viewlets.interfaces import IBelowContentTitle
from plone.app.viewletmanager.manager import OrderedViewletManager
from zope.component import getMultiAdapter


grok.templatedir('viewlets')


class BaseViewlet(grok.Viewlet):
    """Base class for all the viewlets"""
    grok.baseclass()
    grok.layer(ICollectiveCartCoreLayer)
    grok.require('zope2.View')


class AddToCartViewlet(BaseViewlet):
    """Viewlet to show add to cart form for salable article."""
    grok.context(IArticle)
    grok.name('collective.cart.core.add.to.cart')
    grok.template('add-to-cart')
    grok.view(IViewView)
    grok.viewletmanager(IBelowContentTitle)

    def update(self):
        form = self.request.form
        if form.get('form.addtocart', None) is not None:
            IArticleAdapter(self.context).add_to_cart()
            context_state = getMultiAdapter((self.context, self.request), name="plone_context_state")
            return self.request.response.redirect(context_state.current_base_url())

    @property
    def available(self):
        return IArticleAdapter(self.context).addable_to_cart


class CartViewletManager(OrderedViewletManager, grok.ViewletManager):
    """Viewlet manager for cart view."""
    grok.context(IShoppingSiteRoot)
    grok.layer(ICollectiveCartCoreLayer)
    grok.name('collective.cart.core.cartviewletmanager')


class CartArticlesViewlet(BaseViewlet):
    """Cart Articles Viewlet Class."""
    grok.context(IShoppingSiteRoot)
    grok.name('collective.cart.core.cartarticles')
    grok.template('cart-articles')
    grok.viewletmanager(CartViewletManager)

    def update(self):
        form = self.request.form
        uuid = form.get('form.delete.article', None)
        if uuid is not None:
            self.view.shopping_site.remove_cart_articles(uuid)
            if not self.view.cart_articles:
                return self.request.response.redirect(self.view.url())

    @property
    def articles(self):
        """Returns list of articles to show in cart."""
        return self.view.shopping_site.cart_article_listing


class CartContentViewletManager(OrderedViewletManager, grok.ViewletManager):
    """Viewlet manager for cart view."""
    grok.context(ICart)
    grok.layer(ICollectiveCartCoreLayer)
    grok.name('collective.cart.core.cartcontentviewletmanager')


# class CartContentViewlet(grok.Viewlet, BaseListingObject):
class CartContentViewlet(BaseViewlet):
    """Viewlet to show cart content in cart container."""
    grok.context(ICart)
    grok.name('collective.cart.core.cart-content')
    grok.template('cart-content')
    grok.viewletmanager(CartContentViewletManager)

    # @property
    # def articles(self):
    #     """List of CartArticles within cart."""
    #     result = []
    #     for item in self._listing(ICartArticle):
    #         res = {
    #             'id': item.getId(),
    #             'title': item.Title(),
    #             'url': None,
    #             'modification': self._localized_time(item),
    #         }
    #         obj = item.getObject()
    #         article = ICartArticleAdapter(obj).orig_article
    #         if article:
    #             res['url'] = article.absolute_url()
    #         result.append(res)
    #     return result
