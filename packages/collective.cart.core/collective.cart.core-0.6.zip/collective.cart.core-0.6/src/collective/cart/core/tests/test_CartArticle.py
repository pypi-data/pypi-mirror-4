from collective.cart.core.tests.base import IntegrationTestCase
from collective.cart.core.interfaces import ICartArticle


class CartArticleTestSetup(IntegrationTestCase):
    """TestCase for CartArticle"""

    def test_subclass(self):
        from plone.directives.form import Schema
        self.assertTrue(issubclass(ICartArticle, Schema))

    def test_instance(self):
        from plone.dexterity.content import Container
        instance = self.create_content('collective.cart.core.CartArticle')
        self.assertIsInstance(instance, Container)

    def test_verifyObject(self):
        from collective.cart.core.interfaces import ICartArticle
        from zope.interface.verify import verifyObject
        instance = self.create_content('collective.cart.core.CartArticle')
        self.assertTrue(verifyObject(ICartArticle, instance))

    def test_id(self):
        instance = self.create_content('collective.cart.core.CartArticle', id='1')
        self.assertEqual(instance.id, '1')
