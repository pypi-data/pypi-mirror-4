from Acquisition import aq_inner
from Products.CMFCore.interfaces import IFolderish
from Products.Five.browser import BrowserView
from collective.cart.core.event import MakeShoppingSiteEvent
from collective.cart.core.interfaces import IShoppingSiteRoot
from zope.event import notify
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


class Miscellaneous(BrowserView):

    def make_shopping_site(self):
        """Make context shopping site if it is folder."""
        context = aq_inner(self.context)
        alsoProvides(context, IShoppingSiteRoot)
        context.reindexObject(idxs=['object_provides'])

        notify(MakeShoppingSiteEvent(context))

        url = context.absolute_url()
        return self.request.response.redirect(url)

    def unmake_shopping_site(self):
        """Unmake context shopping site."""
        noLongerProvides(self.context, IShoppingSiteRoot)
        self.context.reindexObject(idxs=['object_provides'])
        url = self.context.absolute_url()
        return self.request.response.redirect(url)

    def is_shopping_site(self):
        return IFolderish.providedBy(
            self.context) and IShoppingSiteRoot.providedBy(self.context)

    def not_shopping_site(self):
        return IFolderish.providedBy(
            self.context) and not IShoppingSiteRoot.providedBy(self.context)
