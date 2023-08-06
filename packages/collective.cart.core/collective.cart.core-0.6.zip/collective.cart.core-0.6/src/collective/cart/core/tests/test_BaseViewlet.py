import unittest


class TestBaseViewlet(unittest.TestCase):

    def test_templatedir(self):
        from collective.cart.core.browser import viewlet
        self.assertEqual(getattr(viewlet, 'grokcore.view.directive.templatedir'), 'viewlets')

    def test_subclass(self):
        from five.grok import Viewlet
        from collective.cart.core.browser.viewlet import BaseViewlet
        self.assertTrue(issubclass(BaseViewlet, Viewlet))
