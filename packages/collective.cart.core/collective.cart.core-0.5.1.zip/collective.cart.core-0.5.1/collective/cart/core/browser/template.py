from Products.CMFCore.utils import getToolByName
from collective.cart.core.interfaces import ICart
from collective.cart.core.interfaces import ICartArticle
from collective.cart.core.interfaces import ICartArticleAdapter
from collective.cart.core.interfaces import ICartContainer
from collective.cart.core.interfaces import IShoppingSite
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.core.browser.interfaces import ICollectiveCartCoreLayer
from five import grok
from plone.app.contentlisting.interfaces import IContentListing
from plone.memoize.instance import memoize


grok.templatedir('templates')


class CartView(grok.View):

    grok.context(IShoppingSiteRoot)
    grok.layer(ICollectiveCartCoreLayer)
    grok.name('cart')
    grok.require('zope2.View')
    grok.template('cart')

    def update(self):
        self.request.set('disable_border', True)
        super(CartView, self).update()

    @property
    def cart_articles(self):
        """List of CartArticles within cart."""
        return IShoppingSite(self.context).cart_articles


class BaseListingView(grok.View):
    grok.baseclass()
    grok.layer(ICollectiveCartCoreLayer)
    grok.name('view')
    grok.require('collective.cart.core.ViewCartContent')

    def _listing(self, interface):
        """List of Cart within Cart Container."""
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {
            'path': {
                'query': '/'.join(self.context.getPhysicalPath()),
                'depth': 1,
            },
            'object_provides': interface.__identifier__,
        }
        return IContentListing(catalog(query))

    @memoize
    def _ulocalized_time(self):
        """Return ulocalized_time method.

        :rtype: method
        """
        translation_service = getToolByName(self.context, 'translation_service')
        return translation_service.ulocalized_time

    def _localized_time(self, item):
        ulocalized_time = self._ulocalized_time()
        return ulocalized_time(item.ModificationDate(), long_format=True, context=self.context)


class CartContainerView(BaseListingView):

    grok.context(ICartContainer)
    grok.template('cart-container')

    @property
    def carts(self):
        result = []
        for item in self._listing(ICart):
            res = {
                'id': item.getId(),
                'title': item.Title(),
                'url': item.getURL(),
                'review_state': item.review_state(),
                'modified': self._localized_time(item),
            }
            result.append(res)
        return result


class CartContentView(BaseListingView):

    grok.context(ICart)
    grok.template('cart-content')

    @property
    def articles(self):
        """List of CartArticles within cart."""
        result = []
        for item in self._listing(ICartArticle):
            res = {
                'id': item.getId(),
                'title': item.Title(),
                'url': None,
                'modification': self._localized_time(item),
            }
            obj = item.getObject()
            article = ICartArticleAdapter(obj).orig_article
            if article:
                res['url'] = article.absolute_url()
            result.append(res)
        return result
