from collective.cart.core import _
from plone.directives import form
from zope.interface import Attribute
from zope.interface import Interface
from zope.schema import Int


class IArticle(form.Schema):
    """Schema for Article content type."""


class ICartContainer(form.Schema):
    """Schema for CartContainer content type."""

    next_cart_id = Int(
        title=_(u'Next Cart ID'),
        default=1,
        min=1)

    def update_next_cart_id():  # pragma: no cover
        """Update next_cart_id"""


class ICart(form.Schema):
    """Schema for Cart content type."""


class ICartArticle(form.Schema):
    """Schema for CartArticle content type."""

    orig_uuid = Attribute('Original UUID for the article.')


class IShoppingSiteRoot(form.Schema):
    """Marker interface for Shopping Site Root."""


class IShoppingSite(Interface):
    """Adapter Interface for Shopping Site."""

    shop = Attribute("Shop Site Root object.")
    cart_container = Attribute("Cart Container object of Shop Site Root.")
    cart = Attribute('Current Cart object.')
    cart_articles = Attribute('List of cart articles within current cart.')

    def get_cart_article(cid):  # pragma: no cover
        """Get cart article by cid."""

    def update_next_cart_id():  # pragma: no cover
        """Update next cart ID for the cart container."""

    def remove_cart_articles(ids):  # pragma: no cover
        """Remove articles of ids from current cart."""


class ICartContainerAdapter(Interface):
    """Adapter Interface for CartContainer."""

    def update_next_cart_id():  # pragma: no cover
        """Update next_cart_id based on numbering_method."""


class IArticleAdapter(Interface):
    """Adapter Interface for Article."""

    addable_to_cart = Attribute('True if the Article is addable to cart.')
    cart_articles = Attribute('Cart Article brains which is originally from this Article.')

    def add_to_cart():  # pragma: no cover
        """Add Article to Cart."""


class ICartArticleAdapter(Interface):
    """Adapter Interface for CartArticle."""

    orig_article = Attribute('Originar Article object.')


class IMakeShoppingSiteEvent(Interface):
    """An event making shopping site."""


class IUnmakeShoppingSiteEvent(Interface):
    """An event unmaking shopping site."""
