# -*- coding: utf-8 -*-
from collective.cart.core.interfaces import IShoppingSite
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.core.tests.base import IntegrationTestCase
from plone.dexterity.utils import createContentInContainer
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
from zope.lifecycleevent import modified
from collective.cart.core.adapter.interface import ShoppingSite

import mock


class ShoppingSiteTestCase(IntegrationTestCase):
    """TestCase for ShoppingSite"""

    def test_subclass(self):
        from collective.base.adapter import Adapter
        self.assertTrue(issubclass(ShoppingSite, Adapter))
        from collective.base.interfaces import IAdapter
        self.assertTrue(issubclass(IShoppingSite, IAdapter))

    def test_provides(self):
        self.assertEqual(getattr(ShoppingSite, 'grokcore.component.directive.provides'), IShoppingSite)

    def test_instance(self):
        self.assertIsInstance(IShoppingSite(self.portal), ShoppingSite)

    def test_instance__provides(self):
        self.assertEqual(getattr(IShoppingSite(self.portal), 'grokcore.component.directive.provides'), IShoppingSite)

    def test_shop(self):
        folder1 = self.create_atcontent('Folder', id='folder1')
        folder2 = self.create_atcontent('Folder', folder1, id='folder2')
        folder3 = self.create_atcontent('Folder', folder2, id='folder3')
        alsoProvides(folder1, IShoppingSiteRoot)
        self.assertIsNone(IShoppingSite(self.portal).shop)
        self.assertEqual(IShoppingSite(folder1).shop, folder1)
        self.assertEqual(IShoppingSite(folder2).shop, folder1)
        self.assertEqual(IShoppingSite(folder3).shop, folder1)

        alsoProvides(folder2, IShoppingSiteRoot)
        self.assertIsNone(IShoppingSite(self.portal).shop)
        self.assertEqual(IShoppingSite(folder1).shop, folder1)
        self.assertEqual(IShoppingSite(folder2).shop, folder2)
        self.assertEqual(IShoppingSite(folder3).shop, folder2)

    def test_shop_path(self):
        folder1 = self.create_atcontent('Folder', id='folder1')
        folder2 = self.create_atcontent('Folder', folder1, id='folder2')
        folder3 = self.create_atcontent('Folder', folder2, id='folder3')
        alsoProvides(folder1, IShoppingSiteRoot)
        self.assertIsNone(IShoppingSite(self.portal).shop_path)
        self.assertEqual(IShoppingSite(folder1).shop_path, '/plone/folder1')
        self.assertEqual(IShoppingSite(folder2).shop_path, '/plone/folder1')
        self.assertEqual(IShoppingSite(folder3).shop_path, '/plone/folder1')

        alsoProvides(folder2, IShoppingSiteRoot)
        self.assertIsNone(IShoppingSite(self.portal).shop_path)
        self.assertEqual(IShoppingSite(folder1).shop_path, '/plone/folder1')
        self.assertEqual(IShoppingSite(folder2).shop_path, '/plone/folder1/folder2')
        self.assertEqual(IShoppingSite(folder3).shop_path, '/plone/folder1/folder2')

    def test_cart_container(self):
        self.assertIsNone(IShoppingSite(self.portal).cart_container)

        folder = self.create_atcontent('Folder', id='folder')
        self.assertIsNone(IShoppingSite(folder).cart_container)

        alsoProvides(folder, IShoppingSiteRoot)
        self.assertIsNone(IShoppingSite(folder).cart_container)

        container = createContentInContainer(
            folder, 'collective.cart.core.CartContainer', id='container', checkConstraints=False)
        modified(container)
        self.assertEqual(IShoppingSite(folder).cart_container, container)

        noLongerProvides(folder, IShoppingSiteRoot)
        self.assertIsNone(IShoppingSite(folder).cart_container)

    def test_cart(self):
        shopping_site = IShoppingSite(self.portal)
        self.assertIsNone(shopping_site.cart)

        session = shopping_site.getSessionData(create=True)
        session.set('collective.cart.core', 'CART')
        self.assertEqual(shopping_site.cart, 'CART')

    def test_cart_articles(self):
        shopping_site = IShoppingSite(self.portal)
        self.assertIsNone(shopping_site.cart_articles)

        session = shopping_site.getSessionData(create=True)
        session.set('collective.cart.core', {})
        self.assertIsNone(shopping_site.cart_articles)

        session.set('collective.cart.core', {'articles': 'ARTICLES'})
        self.assertEqual(shopping_site.cart_articles, 'ARTICLES')

    def test_cart_article_listing(self):
        shopping_site = IShoppingSite(self.portal)
        self.assertEqual(shopping_site.cart_article_listing, [])

        session = shopping_site.getSessionData(create=True)
        session.set('collective.cart.core', {'articles': {'1': 'ARTICLE1', '2': 'ARTICLE2'}})
        self.assertEqual(shopping_site.cart_article_listing, ['ARTICLE1', 'ARTICLE2'])

    def test_get_cart_article(self):
        shopping_site = IShoppingSite(self.portal)
        self.assertIsNone(shopping_site.get_cart_article('1'))

        session = shopping_site.getSessionData(create=True)
        session.set('collective.cart.core', {'articles': {'1': 'ARTICLE1', '2': 'ARTICLE2'}})

        self.assertIsNone(shopping_site.get_cart_article('3'))
        self.assertEqual(shopping_site.get_cart_article('2'), 'ARTICLE2')

    def test_remove_cart_articles(self):
        shopping_site = IShoppingSite(self.portal)
        session = shopping_site.getSessionData(create=True)
        session.set('collective.cart.core', {'articles': {'1': 'ARTICLE1', '2': 'ARTICLE2', '3': 'ARTICLE3'}})

        shopping_site.remove_cart_articles('4')
        self.assertEqual(shopping_site.cart_articles, {'1': 'ARTICLE1', '2': 'ARTICLE2', '3': 'ARTICLE3'})

        shopping_site.remove_cart_articles(['2', '3'])
        self.assertEqual(shopping_site.cart_articles, {'1': 'ARTICLE1'})

        shopping_site.remove_cart_articles('1')
        self.assertEqual(shopping_site.cart_articles, {})

    def test_update_cart(self):
        adapter = IShoppingSite(self.portal)
        adapter.update_cart('name', 'NAME')
        self.assertIsNone(adapter.getSessionData(create=False))

        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {})
        adapter.update_cart('name', 'NAME')
        self.assertEqual(session.get('collective.cart.core'), {'name': 'NAME'})

    def test_remove_from_cart(self):
        adapter = IShoppingSite(self.portal)
        self.assertIsNone(adapter.cart)
        self.assertIsNone(adapter.remove_from_cart('name'))
        self.assertIsNone(adapter.cart)

        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {})
        self.assertEqual(adapter.cart, {})
        self.assertIsNone(adapter.remove_from_cart('name'))
        self.assertEqual(adapter.cart, {})

        session.set('collective.cart.core', {'name': 'Name'})
        self.assertEqual(adapter.cart, {'name': 'Name'})
        self.assertEqual(adapter.remove_from_cart('name'), 'Name')
        self.assertEqual(adapter.cart, {})

    def test_clear_cart(self):
        shopping_site = IShoppingSite(self.portal)
        self.assertIsNone(shopping_site.clear_cart())

        session = shopping_site.getSessionData(create=True)
        session.set('collective.cart.core', {'articles': {'1': 'ARTICLE1'}})
        self.assertIsNone(shopping_site.clear_cart())
        self.assertIsNone(session.get('collective.cart.core'))

        session.set('collective.cart.core', {'articles': {'1': 'ARTICLE1'}})
        self.assertIsNone(shopping_site.clear_cart('KEY'))
        self.assertEqual(session.get('collective.cart.core'), {'articles': {'1': 'ARTICLE1'}})

        self.assertEqual(shopping_site.clear_cart('articles'), {'1': 'ARTICLE1'})
        self.assertEqual(session.get('collective.cart.core'), {})

    # CartContainer related methods

    def test_get_cart(self):
        self.assertIsNone(IShoppingSite(self.portal).get_cart('1'))

        folder = self.create_atcontent('Folder', id='folder')
        alsoProvides(folder, IShoppingSiteRoot)
        container = createContentInContainer(
            folder, 'collective.cart.core.CartContainer', id='container', checkConstraints=False)
        modified(container)
        self.assertIsNone(IShoppingSite(folder).get_cart('1'))

        cart1 = createContentInContainer(
            container, 'collective.cart.core.Cart', id='1', checkConstraints=False)
        modified(cart1)
        self.assertIsNone(IShoppingSite(folder).get_cart('2'))
        self.assertEqual(IShoppingSite(folder).get_cart('1'), cart1)

    def create_cart_container(self, context):
        container = createContentInContainer(
            context, 'collective.cart.core.CartContainer', id='cart-container', checkConstraints=False)
        modified(container)
        return container

    @mock.patch('collective.cart.core.adapter.interface.ICartContainerAdapter')
    def test_update_next_cart_id(self, ICartContainerAdapter):
        folder = self.create_atcontent('Folder', id='folder')
        alsoProvides(folder, IShoppingSiteRoot)
        adapter = IShoppingSite(folder)
        adapter.update_next_cart_id()
        self.assertFalse(ICartContainerAdapter.called)

        self.create_cart_container(folder)
        adapter.update_next_cart_id()
        self.assertTrue(ICartContainerAdapter.called)

    def test_create_cart(self):
        folder = self.create_atcontent('Folder', id='folder')
        adapter = IShoppingSite(folder)
        adapter.create_cart()
        self.assertIsNone(adapter.get_cart('1'))

        alsoProvides(folder, IShoppingSiteRoot)
        adapter.create_cart()
        self.assertIsNone(adapter.get_cart('1'))

        self.create_cart_container(folder)
        adapter.create_cart()
        self.assertIsNone(adapter.get_cart('1'))

        items = {
            'id': '1',
            'title': 'Ärticle1',
            'description': 'Description of Ärticle1',
        }

        session = adapter.getSessionData(create=True)
        session.set('collective.cart.core', {'articles': {'1': items}})

        self.assertEqual(adapter.cart_container.next_cart_id, 1)
        adapter.create_cart()
        cart = adapter.get_cart('1')
        self.assertIsNotNone(cart)

        carticle = cart.get('1')
        self.assertEqual(carticle.title, items['title'])
        self.assertEqual(carticle.description, items['description'])

        adapter.create_cart('4')
        cart = adapter.get_cart('4')
        self.assertIsNotNone(cart)

        carticle = cart.get('1')
        self.assertEqual(carticle.title, items['title'])
        self.assertEqual(carticle.description, items['description'])
