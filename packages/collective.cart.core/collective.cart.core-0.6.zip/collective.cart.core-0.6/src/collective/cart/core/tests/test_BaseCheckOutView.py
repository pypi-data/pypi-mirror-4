# -*- coding: utf-8 -*-
from collective.cart.core.browser.template import BaseCheckOutView
from collective.cart.core.tests.base import IntegrationTestCase

import mock


class BaseCheckOutViewTestCase(IntegrationTestCase):
    """TestCase for BaseCheckOutView"""

    def test_subclass(self):
        from collective.cart.core.browser.template import BaseView
        self.assertTrue(issubclass(BaseCheckOutView, BaseView))

    def test_baseclass(self):
        self.assertTrue(getattr(BaseCheckOutView, 'martian.martiandirective.baseclass'))

    def test_shopping_site(self):
        from collective.cart.core.adapter.interface import ShoppingSite
        instance = self.create_view(BaseCheckOutView)
        self.assertIsInstance(instance.shopping_site, ShoppingSite)

    def test_cart_articles(self):
        from collective.cart.core.interfaces import IArticleAdapter
        instance = self.create_view(BaseCheckOutView)
        self.assertIsNone(instance.cart_articles)

        article = self.create_content('collective.cart.core.Article')
        IArticleAdapter(article).add_to_cart()
        self.assertEqual(len(instance.cart_articles), 1)

    def test_update(self):
        from collective.cart.core.interfaces import IArticleAdapter
        from plone.uuid.interfaces import IUUID
        instance = self.create_view(BaseCheckOutView)
        instance.request = mock.Mock()
        instance.update()
        instance.request.set.assert_called_with('disable_border', True)
        instance.request.response.redirect.assert_called_with('http://nohost/plone/@@cart')

        article1 = self.create_content('collective.cart.core.Article', id='article1')
        IArticleAdapter(article1).add_to_cart()
        article2 = self.create_content('collective.cart.core.Article', id='article2')
        IArticleAdapter(article2).add_to_cart()
        instance.update()
        instance.request.set.assert_called_with('disable_border', True)
        self.assertEqual(len(instance.cart_articles), 2)

        # Remove article1
        self.portal.manage_delObjects(['article1'])
        instance.update()
        instance.request.set.assert_called_with('disable_border', True)
        self.assertEqual(instance.cart_articles.keys(), [IUUID(article2)])

        # Remove article2
        self.portal.manage_delObjects(['article2'])
        instance.update()
        instance.request.set.assert_called_with('disable_border', True)
        instance.request.response.redirect.assert_called_with('http://nohost/plone/@@cart')
