# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from collective.cart.core.adapter.article import ArticleAdapter
from collective.cart.core.interfaces import IArticleAdapter
from collective.cart.core.tests.base import IntegrationTestCase
from plone.dexterity.utils import createContentInContainer
from zope.lifecycleevent import modified

import mock


class TestArticleAdapter(IntegrationTestCase):
    """TestCase for ArticleAdapter"""

    def test_subclass(self):
        from collective.base.adapter import Adapter
        self.assertTrue(issubclass(ArticleAdapter, Adapter))
        from collective.base.interfaces import IAdapter
        self.assertTrue(issubclass(IArticleAdapter, IAdapter))

    def test_context(self):
        from collective.cart.core.interfaces import IArticle
        self.assertEqual(getattr(ArticleAdapter, 'grokcore.component.directive.context'), IArticle)

    def test_provides(self):
        self.assertEqual(getattr(ArticleAdapter, 'grokcore.component.directive.provides'), IArticleAdapter)

    def create_article(self, number=1):
        """Create cart."""
        articles = []
        for num in range(1, number + 1):
            oid = 'article{}'.format(num)
            title = 'Ärticle{}'.format(num)
            description = "Descriptiön of Ärticle{}".format(num)
            article = createContentInContainer(self.portal, 'collective.cart.core.Article', checkConstraints=False,
                id=oid, title=title, description=description)
            modified(article)
            articles.append(article)
        if len(articles) == 1:
            return articles[0]
        return articles

    def test_instance(self):
        article = self.create_article()
        self.assertIsInstance(IArticleAdapter(article), ArticleAdapter)

    def test_instance__context(self):
        from collective.cart.core.interfaces import IArticle
        article = self.create_article()
        self.assertEqual(getattr(IArticleAdapter(article), 'grokcore.component.directive.context'), IArticle)

    def test_instance__provides(self):
        article = self.create_article()
        self.assertEqual(getattr(IArticleAdapter(article), 'grokcore.component.directive.provides'), IArticleAdapter)

    def test_addable_to_cart(self):
        from collective.cart.core.interfaces import IShoppingSiteRoot
        from zope.interface import alsoProvides
        article = self.create_article()
        self.assertFalse(IArticleAdapter(article).addable_to_cart)

        alsoProvides(self.portal, IShoppingSiteRoot)
        self.assertTrue(IArticleAdapter(article).addable_to_cart)

        article.salable = False
        self.assertFalse(IArticleAdapter(article).addable_to_cart)

    def test_add_to_cart(self):
        from plone.uuid.interfaces import IUUID
        session_data_manager = getToolByName(self.portal, 'session_data_manager')
        session = session_data_manager.getSessionData(create=False)
        self.assertIsNone(session)

        articles = self.create_article(2)
        article1 = articles[0]
        uuid1 = IUUID(article1)
        article2 = articles[1]
        uuid2 = IUUID(article2)
        adapter = IArticleAdapter(article1)
        adapter._update_existing_cart_article = mock.Mock()
        adapter.add_to_cart()
        session = session_data_manager.getSessionData(create=False)
        self.assertEqual(len(session.get('collective.cart.core').get('articles')), 1)
        self.assertEqual(sorted(session.get('collective.cart.core').get('articles').get(uuid1).items()),
            [
                ('description', 'Descriptiön of Ärticle1'),
                ('id', uuid1),
                ('title', 'Ärticle1'),
                ('url', 'http://nohost/plone/article1')])
        self.assertFalse(adapter._update_existing_cart_article.called)

        adapter.add_to_cart()
        self.assertEqual(len(session.get('collective.cart.core').get('articles')), 1)
        self.assertEqual(sorted(session.get('collective.cart.core').get('articles').get(uuid1).items()),
            [
                ('description', 'Descriptiön of Ärticle1'),
                ('id', uuid1),
                ('title', 'Ärticle1'),
                ('url', 'http://nohost/plone/article1')])
        self.assertTrue(adapter._update_existing_cart_article.called)

        adapter = IArticleAdapter(article2)
        adapter.add_to_cart()
        self.assertEqual(len(session.get('collective.cart.core').get('articles')), 2)
        self.assertEqual(sorted(session.get('collective.cart.core').get('articles').get(uuid1).items()),
            [
                ('description', 'Descriptiön of Ärticle1'),
                ('id', uuid1),
                ('title', 'Ärticle1'),
                ('url', 'http://nohost/plone/article1')])
        self.assertEqual(sorted(session.get('collective.cart.core').get('articles').get(uuid2).items()),
            [
                ('description', 'Descriptiön of Ärticle2'),
                ('id', uuid2),
                ('title', 'Ärticle2'),
                ('url', 'http://nohost/plone/article2')])
