from collective.cart.core.tests.base import IntegrationTestCase
from plone.dexterity.utils import createContentInContainer
from zope.lifecycleevent import modified


class TestCartAdapter(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_subclass(self):
        from collective.base.adapter import Adapter
        from collective.cart.core.adapter.cart import CartAdapter
        self.assertTrue(issubclass(CartAdapter, Adapter))
        from collective.base.interfaces import IAdapter
        from collective.cart.core.interfaces import ICartAdapter
        self.assertTrue(issubclass(ICartAdapter, IAdapter))

    def test_context(self):
        from collective.cart.core.adapter.cart import CartAdapter
        from collective.cart.core.interfaces import ICart
        self.assertEqual(getattr(CartAdapter, 'grokcore.component.directive.context'), ICart)

    def test_provides(self):
        from collective.cart.core.adapter.cart import CartAdapter
        from collective.cart.core.interfaces import ICartAdapter
        self.assertEqual(getattr(CartAdapter, 'grokcore.component.directive.provides'), ICartAdapter)

    def create_cart(self):
        """Create cart."""
        cart = createContentInContainer(self.portal, 'collective.cart.core.Cart', id='1',
            checkConstraints=False)
        modified(cart)
        return cart

    def test_instance(self):
        from collective.cart.core.adapter.cart import CartAdapter
        from collective.cart.core.interfaces import ICartAdapter
        cart = self.create_cart()
        self.assertIsInstance(ICartAdapter(cart), CartAdapter)

    def test_instance__context(self):
        from collective.cart.core.interfaces import ICart
        from collective.cart.core.interfaces import ICartAdapter
        cart = self.create_cart()
        self.assertEqual(getattr(ICartAdapter(cart), 'grokcore.component.directive.context'), ICart)

    def test_instance__provides(self):
        from collective.cart.core.interfaces import ICartAdapter
        cart = self.create_cart()
        self.assertEqual(getattr(ICartAdapter(cart), 'grokcore.component.directive.provides'), ICartAdapter)

    def test_articles__None(self):
        """Test property: articles when there are no articles in the cart."""
        from collective.cart.core.interfaces import ICartAdapter
        cart = self.create_cart()
        self.assertEqual(len(ICartAdapter(cart).articles), 0)

    def test_articles__Two(self):
        """Test property: articles when there are two articles in the cart."""
        from collective.cart.core.interfaces import ICartAdapter
        cart = self.create_cart()
        article1 = createContentInContainer(cart, 'collective.cart.core.CartArticle',
            id='1', checkConstraints=False)
        modified(article1)
        article2 = createContentInContainer(cart, 'collective.cart.core.CartArticle',
            id='2', checkConstraints=False)
        modified(article2)
        self.assertEqual(len(ICartAdapter(cart).articles), 2)

    def test_get_article(self):
        from collective.cart.core.interfaces import ICartAdapter
        cart = self.create_cart()
        self.assertIsNone(ICartAdapter(cart).get_article('1'))

        article1 = createContentInContainer(cart, 'collective.cart.core.CartArticle',
            id='1', checkConstraints=False)
        modified(article1)
        self.assertIsNone(ICartAdapter(cart).get_article('2'))
        self.assertEqual(ICartAdapter(cart).get_article('1'), article1)
