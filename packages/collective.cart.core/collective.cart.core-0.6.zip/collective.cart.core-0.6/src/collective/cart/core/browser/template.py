from Products.CMFCore.utils import getToolByName
from collective.cart.core.browser.interfaces import ICollectiveCartCoreLayer
from collective.cart.core.interfaces import ICart
from collective.cart.core.interfaces import ICartContainer
from collective.cart.core.interfaces import ICartContainerAdapter
from collective.cart.core.interfaces import IShoppingSite
from collective.cart.core.interfaces import IShoppingSiteRoot
from five import grok
from zope.lifecycleevent import modified


grok.templatedir('templates')


class BaseView(grok.View):
    """Base class for View"""
    grok.baseclass()
    grok.context(IShoppingSiteRoot)
    grok.layer(ICollectiveCartCoreLayer)
    grok.require('zope2.View')


class BaseCheckOutView(BaseView):
    """Base class for check out view"""
    grok.baseclass()

    def update(self):
        self.request.set('disable_border', True)

        if self.cart_articles:
            articles = self.cart_articles.copy()
            number_of_articles = len(articles)
            for key in self.cart_articles:
                if not self.shopping_site.get_brain(UID=key):
                    del articles[key]

            if len(articles) != number_of_articles:
                session = self.shopping_site.getSessionData(create=False)
                if session:
                    session.set('collective.cart.core', {'articles': articles})

        else:
            cart_url = '{}/@@cart'.format(self.context.absolute_url())
            current_base_url = self.context.restrictedTraverse("plone_context_state").current_base_url()
            if cart_url != current_base_url:
                return self.request.response.redirect(cart_url)

    @property
    def shopping_site(self):
        return IShoppingSite(self.context)

    @property
    def cart_articles(self):
        """List of CartArticles within cart."""
        return self.shopping_site.cart_articles


class CartView(BaseCheckOutView):
    """Cart View"""
    grok.name('cart')
    grok.template('cart')


class OrdersView(BaseView):
    grok.name('orders')
    grok.require('collective.cart.core.ViewCartContent')
    grok.template('orders')

    @property
    def cart_container(self):
        if ICartContainer.providedBy(self.context):
            return self.context
        return IShoppingSite(self.context).cart_container

    def transitions(self, item):
        workflow = getToolByName(self.context, 'portal_workflow')
        obj = item.getObject()
        res = []
        for trans in workflow.getTransitionsFor(obj):
            available = True
            if item.review_state() == 'created' and trans['id'] != 'canceled':
                available = False
            res.append({
                'id': trans['id'],
                'name': trans['name'],
                'available': available,
            })
        return res

    @property
    def carts(self):
        if self.cart_container:
            result = []
            workflow = getToolByName(self.context, 'portal_workflow')
            adapter = ICartContainerAdapter(self.cart_container)
            for item in adapter.get_content_listing(ICart, sort_on="modified", sort_order="descending"):
                res = {
                    'id': item.getId(),
                    'title': item.Title(),
                    'url': item.getURL(),
                    'state_title': workflow.getTitleForStateOnType(item.review_state(), item.portal_type),
                    'modified': adapter.ulocalized_time(item.ModificationDate()),
                    'owner': item.Creator(),
                    'transitions': self.transitions(item),
                    'is_canceled': item.review_state() == 'canceled',
                }
                result.append(res)
            return result

    def update(self):
        self.request.set('disable_plone.leftcolumn', True)
        self.request.set('disable_plone.rightcolumn', True)

        form = self.request.form
        value = form.get('form.buttons.ChangeState')
        cart_id = form.get('cart-id')

        if value is not None and cart_id is not None:
            cart = IShoppingSite(self.context).get_cart(cart_id)
            if cart:
                workflow = getToolByName(self.context, 'portal_workflow')
                workflow.doActionFor(cart, value)
                modified(cart)

        elif form.get('form.buttons.RemoveCart') is not None and cart_id is not None:
            self.cart_container.manage_delObjects([cart_id])


class CartContainerView(OrdersView):
    """View for CartContainer."""
    grok.context(ICartContainer)
    grok.name('view')


class CartContentView(BaseView):
    """View for CartContent"""
    grok.context(ICart)
    grok.name('view')
    grok.require('collective.cart.core.ViewCartContent')
    grok.template('cart-content')
