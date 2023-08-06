# -*- coding: utf-8 -*-
from collective.cart.core.tests.base import IntegrationTestCase
from zope.publisher.browser import TestRequest

import mock


class TestCartArticlesViewlet(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_subclass(self):
        from collective.cart.core.browser.viewlet import CartArticlesViewlet
        from collective.cart.core.browser.viewlet import BaseViewlet
        self.assertTrue(issubclass(CartArticlesViewlet, BaseViewlet))

    def create_instance(self):
        from collective.cart.core.browser.viewlet import CartArticlesViewlet
        return CartArticlesViewlet(self.portal, TestRequest(), None, None)

    def test_instance__context(self):
        from collective.cart.core.interfaces import IShoppingSiteRoot
        instance = self.create_instance()
        self.assertEqual(getattr(instance, 'grokcore.component.directive.context'), IShoppingSiteRoot)

    def test_instance__name(self):
        instance = self.create_instance()
        self.assertEqual(getattr(instance, 'grokcore.component.directive.name'), 'collective.cart.core.cartarticles')

    def test_instance__template(self):
        instance = self.create_instance()
        self.assertEqual(getattr(instance, 'grokcore.view.directive.template'), 'cart-articles')

    def test_instance__viewletmanager(self):
        from collective.cart.core.browser.viewlet import CartViewletManager
        instance = self.create_instance()
        self.assertEqual(getattr(instance, 'grokcore.viewlet.directive.viewletmanager'), CartViewletManager)

    def test_articles(self):
        instance = self.create_instance()
        instance.view = mock.Mock()
        shopping_site = mock.Mock()
        instance.view.shopping_site = shopping_site
        self.assertEqual(instance.articles, shopping_site.cart_article_listing)

    def test_update(self):
        instance = self.create_instance()
        instance.view = mock.Mock()
        instance.update()
        self.assertFalse(instance.view.shopping_site.remove_cart_articles.called)

        instance.request = mock.Mock()
        instance.request.form = {'form.delete.article': 'UUID'}
        instance.update()
        self.assertTrue(instance.view.shopping_site.remove_cart_articles.called)
        self.assertFalse(instance.request.response.redirect.called)

        instance.view.cart_articles = []
        instance.update()
        self.assertTrue(instance.view.shopping_site.remove_cart_articles.called)
        self.assertTrue(instance.request.response.redirect.called)
