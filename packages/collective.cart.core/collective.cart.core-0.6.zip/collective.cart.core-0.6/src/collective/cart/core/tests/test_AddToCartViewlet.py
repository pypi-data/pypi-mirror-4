# -*- coding: utf-8 -*-
from collective.cart.core.tests.base import IntegrationTestCase
from plone.dexterity.utils import createContentInContainer
from zope.lifecycleevent import modified
from zope.publisher.browser import TestRequest

import mock


class TestAddToCartViewlet(IntegrationTestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def test_subclass(self):
        from collective.cart.core.browser.viewlet import AddToCartViewlet
        from collective.cart.core.browser.viewlet import BaseViewlet
        self.assertTrue(issubclass(AddToCartViewlet, BaseViewlet))

    def create_instance(self):
        from collective.cart.core.browser.viewlet import AddToCartViewlet
        article = createContentInContainer(self.portal, 'collective.cart.core.Article', checkConstraints=False,
            id='article', title='Ärticle1', description='Descriptiön of Ärticle1')
        modified(article)

        return AddToCartViewlet(article, TestRequest(), None, None)

    def test_instance__context(self):
        from collective.cart.core.interfaces import IArticle
        instance = self.create_instance()
        self.assertEqual(getattr(instance, 'grokcore.component.directive.context'), IArticle)

    def test_instance__layer(self):
        from collective.cart.core.browser.interfaces import ICollectiveCartCoreLayer
        instance = self.create_instance()
        self.assertEqual(getattr(instance, 'grokcore.view.directive.layer'), ICollectiveCartCoreLayer)

    def test_instance__name(self):
        instance = self.create_instance()
        self.assertEqual(getattr(instance, 'grokcore.component.directive.name'), 'collective.cart.core.add.to.cart')

    def test_instance__require(self):
        instance = self.create_instance()
        self.assertEqual(getattr(instance, 'grokcore.security.directive.require'), ['zope2.View'])

    def test_instance__template(self):
        instance = self.create_instance()
        self.assertEqual(getattr(instance, 'grokcore.view.directive.template'), 'add-to-cart')

    def test_instance__view(self):
        from plone.app.layout.globals.interfaces import IViewView
        instance = self.create_instance()
        self.assertEqual(getattr(instance, 'grokcore.viewlet.directive.view'), IViewView)

    def test_instance__viewletmanager(self):
        from plone.app.layout.viewlets.interfaces import IBelowContentTitle
        instance = self.create_instance()
        self.assertEqual(getattr(instance, 'grokcore.viewlet.directive.viewletmanager'), IBelowContentTitle)

    @mock.patch('collective.cart.core.browser.viewlet.IArticleAdapter')
    def test_available(self, IArticleAdapter):
        IArticleAdapter().addable_to_cart = 'AVAILABLE'
        instance = self.create_instance()
        self.assertEqual(instance.available, 'AVAILABLE')

    @mock.patch('collective.cart.core.browser.viewlet.getMultiAdapter')
    @mock.patch('collective.cart.core.browser.viewlet.IArticleAdapter')
    def test_update(self, IArticleAdapter, getMultiAdapter):
        instance = self.create_instance()
        instance.request = mock.Mock()
        instance.request.form = {}
        instance.update()
        self.assertFalse(IArticleAdapter().add_to_cart.called)
        self.assertFalse(instance.request.response.redirect.called)

        instance.request.form = {'form.addtocart': True}
        instance.update()
        self.assertTrue(IArticleAdapter().add_to_cart.called)
        self.assertTrue(instance.request.response.redirect.called)
