from Products.CMFCore.utils import getToolByName
from plone.app.contentlisting.interfaces import IContentListing
from plone.memoize.instance import memoize


class BaseListingObject(object):
    """Base class which provides base methods."""

    def _listing(self, interface):
        """List of Cart within Cart Container."""
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {
            'path': {
                'query': '/'.join(self.context.getPhysicalPath()),
                'depth': 1,
            },
            'object_provides': interface.__identifier__,
        }
        return IContentListing(catalog(query))

    @memoize
    def _ulocalized_time(self):
        """Return ulocalized_time method.

        :rtype: method
        """
        translation_service = getToolByName(self.context, 'translation_service')
        return translation_service.ulocalized_time

    def _localized_time(self, item, long_format=True):
        ulocalized_time = self._ulocalized_time()
        return ulocalized_time(item.ModificationDate(),
            long_format=long_format, context=self.context)
