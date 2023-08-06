from collections import OrderedDict
from collective.cart.core.interfaces import ISessionArticles
from zope.interface import implements


class SessionArticles(OrderedDict):
    implements(ISessionArticles)
