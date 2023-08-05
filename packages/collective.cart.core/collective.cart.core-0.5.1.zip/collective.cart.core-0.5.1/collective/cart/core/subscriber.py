from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.statusmessages.interfaces import IStatusMessage
from collective.cart.core import _
from collective.cart.core.interfaces import ICartContainer
from collective.cart.core.interfaces import IMakeShoppingSiteEvent
from collective.cart.core.interfaces import IShoppingSite
from collective.cart.core.interfaces import IShoppingSiteRoot
from five import grok
from plone.dexterity.utils import createContentInContainer
from zope.interface import noLongerProvides
from zope.lifecycleevent import modified
from zope.lifecycleevent.interfaces import IObjectRemovedEvent


@grok.subscribe(ICartContainer, IObjectRemovedEvent)
def unmake_shopping_site(container, event):
    if container == event.object:
        parent = aq_parent(aq_inner(container))
        noLongerProvides(parent, IShoppingSiteRoot)
        parent.reindexObject(idxs=['object_provides'])
        message = _(u"This container is no longer a shopping site.")
        IStatusMessage(container.REQUEST).addStatusMessage(message, type='warn')


@grok.subscribe(IMakeShoppingSiteEvent)
def add_cart_container(event):
    context = event.context
    if not IShoppingSite(context).cart_container:
        container = createContentInContainer(
            context, 'collective.cart.core.CartContainer',
            id="cart-container", title="Cart Container", checkConstraints=False)
        modified(container)
