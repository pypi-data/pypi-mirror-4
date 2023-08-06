from collective.base.adapter import Adapter
from collective.cart.core.interfaces import ICartArticle
from collective.cart.core.interfaces import ICartArticleAdapter
from five import grok


class CartArticleAdapter(Adapter):
    """Adapter to handle CartArticle."""

    grok.context(ICartArticle)
    grok.provides(ICartArticleAdapter)

    @property
    def orig_article(self):
        """Returns riginar Article object."""
        uuid = getattr(self.context, 'orig_uuid', None)
        if uuid is None:
            uuid = self.context.id
        return self.get_object(path=self.portal_path, UID=uuid)
