from collective.base.interfaces import IAdapter
from collective.cart.core import _
from plone.directives import form
from zope.interface import Attribute
from zope.interface import Interface
from zope import schema


class IArticle(form.Schema):
    """Schema for Article content type."""


class ICartContainer(form.Schema):
    """Schema for CartContainer content type."""

    next_cart_id = schema.Int(
        title=_(u'Next Cart ID'),
        default=1,
        min=1)

    def update_next_cart_id():  # pragma: no cover
        """Update next_cart_id"""

    def clear_created(minutes):  # pragma: no cover
        """Clear cart state with created if it is older than minutes"""


class ICart(form.Schema):
    """Schema for Cart content type."""

    description = schema.Text(
        title=_(u'Description'),
        required=False)


class ICartArticle(form.Schema):
    """Schema for CartArticle content type."""

    # orig_uuid = Attribute('Original UUID')


class IShoppingSiteRoot(form.Schema):
    """Marker interface for Shopping Site Root."""


class IShoppingSite(IAdapter):
    """Adapter Interface for Shopping Site."""

    shop = Attribute("Shop Site Root object.")
    shop_path = Attribute("Path of shop.")
    cart_container = Attribute("Cart Container object located directly under Shop Site Root.")
    cart = Attribute('Current cart in session.')
    cart_articles = Attribute('List of ordered dictionary of cart articles in session.')
    cart_article_listing = Attribute('List of cart articles in session for views.')

    def get_cart_article(uuid):  # pragma: no cover
        """Get cart article by uuid."""

    def remove_cart_articles(ids):  # pragma: no cover
        """Remove articles of ids from current cart."""

    def update_cart(name, items):  # pragma: no cover
        """Update cart"""

    def remove_from_cart(name):  # pragma: no cover
        """Remove name from cart"""

    def clear_cart(key=None):  # pragma: no cover
        """Clear cart from session"""

    # CartContainer related methods comes here::

    def get_cart(cart_id):  # pragma: no cover
        """Get cart by its id."""

    def update_next_cart_id():  # pragma: no cover
        """Update next cart ID for the cart container."""

    def create_cart(cart_id=None):  # pragma: no cover
        """Create cart instance from cart in session."""


class ICartContainerAdapter(IAdapter):
    """Adapter Interface for CartContainer."""

    def update_next_cart_id():  # pragma: no cover
        """Update next_cart_id based on numbering_method."""


class ICartAdapter(IAdapter):
    """Adapter interface for Cart."""

    articles = Attribute('List of brains of CartArticle.')

    def get_article(oid):
        """Get CartArticle form cart by ID."""


class ICartArticleAdapter(IAdapter):
    """Adapter Interface for CartArticle."""

    orig_article = Attribute('Originar Article object.')


class IArticleAdapter(IAdapter):
    """Adapter Interface for Article."""

    addable_to_cart = Attribute('True if the Article is addable to cart.')

    def add_to_cart():  # pragma: no cover
        """Add Article to Cart."""


class IMakeShoppingSiteEvent(Interface):
    """An event making shopping site."""


class IUnmakeShoppingSiteEvent(Interface):
    """An event unmaking shopping site."""


class ISessionArticles(Interface):
    """Interface for cart in session."""
