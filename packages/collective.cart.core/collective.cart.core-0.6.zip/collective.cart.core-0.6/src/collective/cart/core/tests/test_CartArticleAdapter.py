from collective.cart.core.tests.base import IntegrationTestCase
from plone.dexterity.utils import createContentInContainer
from zope.lifecycleevent import modified


class TestCartArticleAdapter(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_subclass(self):
        from collective.base.adapter import Adapter
        from collective.cart.core.adapter.cartarticle import CartArticleAdapter
        self.assertTrue(issubclass(CartArticleAdapter, Adapter))
        from collective.base.interfaces import IAdapter
        from collective.cart.core.interfaces import ICartArticleAdapter
        self.assertTrue(issubclass(ICartArticleAdapter, IAdapter))

    def test_context(self):
        from collective.cart.core.adapter.cartarticle import CartArticleAdapter
        from collective.cart.core.interfaces import ICartArticle
        self.assertEqual(getattr(CartArticleAdapter, 'grokcore.component.directive.context'), ICartArticle)

    def test_provides(self):
        from collective.cart.core.adapter.cartarticle import CartArticleAdapter
        from collective.cart.core.interfaces import ICartArticleAdapter
        self.assertEqual(getattr(CartArticleAdapter, 'grokcore.component.directive.provides'), ICartArticleAdapter)

    def create_cart_article(self, uuid=None):
        """Create cart."""
        cart = createContentInContainer(self.portal, 'collective.cart.core.Cart', id='1',
            checkConstraints=False)
        modified(cart)
        if uuid is None:
            uuid = '1'
        article = createContentInContainer(cart, 'collective.cart.core.CartArticle', id=uuid,
            checkConstraints=False)
        modified(article)
        return article

    def test_instance(self):
        from collective.cart.core.adapter.cartarticle import CartArticleAdapter
        from collective.cart.core.interfaces import ICartArticleAdapter
        article = self.create_cart_article()
        self.assertIsInstance(ICartArticleAdapter(article), CartArticleAdapter)

    def test_instance__context(self):
        from collective.cart.core.interfaces import ICartArticle
        from collective.cart.core.interfaces import ICartArticleAdapter
        article = self.create_cart_article()
        self.assertEqual(getattr(ICartArticleAdapter(article), 'grokcore.component.directive.context'), ICartArticle)

    def test_instance__provides(self):
        from collective.cart.core.interfaces import ICartArticleAdapter
        article = self.create_cart_article()
        self.assertEqual(getattr(ICartArticleAdapter(article), 'grokcore.component.directive.provides'), ICartArticleAdapter)

    def test_orig_article__orig_uuid(self):
        from collective.cart.core.interfaces import ICartArticleAdapter
        from plone.uuid.interfaces import IUUID
        carticle = self.create_cart_article()
        self.assertIsNone(ICartArticleAdapter(carticle).orig_article)

        article = createContentInContainer(self.portal, 'collective.cart.core.Article', id='article',
            checkConstraints=False)
        modified(article)
        uuid = IUUID(article)

        setattr(carticle, 'orig_uuid', uuid)
        modified(carticle)
        self.assertEqual(ICartArticleAdapter(carticle).orig_article, article)

    def test_orig_article__orig_uuid__None(self):
        from collective.cart.core.interfaces import ICartArticleAdapter
        from plone.uuid.interfaces import IUUID
        article = createContentInContainer(self.portal, 'collective.cart.core.Article', id='article',
            checkConstraints=False)
        modified(article)
        uuid = IUUID(article)
        carticle = self.create_cart_article(uuid)
        self.assertEqual(ICartArticleAdapter(carticle).orig_article, article)
