from collective.cart.core.interfaces import IMakeShoppingSiteEvent
from collective.cart.core.interfaces import IUnmakeShoppingSiteEvent
from zope.interface import implements


class BaseEvent(object):

    def __init__(self, context):
        self.context = context


class MakeShoppingSiteEvent(BaseEvent):
    implements(IMakeShoppingSiteEvent)


class UnmakeShoppingSiteEvent(BaseEvent):
    implements(IUnmakeShoppingSiteEvent)
