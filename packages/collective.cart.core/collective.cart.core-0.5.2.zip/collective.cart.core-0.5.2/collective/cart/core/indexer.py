from collective.cart.core.interfaces import ICartArticle
from five import grok
from plone.indexer import indexer
from plone.uuid.interfaces import IUUID


@grok.adapter(ICartArticle, name='orig_uuid')
@indexer(ICartArticle)
def original_uuid(context):
    return IUUID(context)
