from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from collective.base.interfaces import IBaseAdapter
from five import grok
from plone.app.contentlisting.interfaces import IContentListing
from plone.memoize.instance import memoize
from zope.interface import Interface


class BaseAdapter(grok.Adapter):
    """Base class for adapters"""

    grok.context(Interface)
    grok.provides(IBaseAdapter)

    @property
    @memoize
    def catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def context_path(self):
        return '/'.join(aq_inner(self.context).getPhysicalPath())

    def get_brains(self, interfaces=None, **query):
        """In default, find from path under the context."""

        # Interfaces
        if interfaces is not None:
            if not isinstance(interfaces, list):
                interfaces = [interfaces]
            object_provides = query.get('object_provides') or []
            if not isinstance(object_provides, list):
                object_provides = [object_provides]
            query['object_provides'] = [interface.__identifier__ for interface in interfaces] + object_provides

        # Set default path
        path = query.get('path')
        if path is None:
            path = self.context_path

        # Depth
        depth = query.get('depth')
        if depth:
            path = {'query': path, 'depth': depth}
        query['path'] = path
        sort_limit = query.get('sort_limit')

        # Unrestricted
        unrestricted = query.get('unrestricted')
        catalog = self.catalog
        if unrestricted:
            catalog = self.catalog.unrestrictedSearchResults

        brains = catalog(query)
        if sort_limit:
            return brains[:sort_limit]
        return brains

    def get_brain(self, interfaces=None, **query):
        brains = self.get_brains(interfaces=interfaces, **query)
        if brains:
            return brains[0]

    def get_object(self, interfaces=None, **query):
        brain = self.get_brain(interfaces=interfaces, **query)
        if brain:
            return brain.getObject()

    def get_content_listing(self, interfaces=None, **query):
        return IContentListing(self.get_brains(interfaces=interfaces, **query))

    @property
    @memoize
    def ulocalized_time(self):
        """Return ulocalized_time method.

        :rtype: method
        """
        return getToolByName(self.context, 'translation_service').ulocalized_time

    @property
    @memoize
    def getSessionData(self):
        """Returns getSessionData method.

        :rtype: method
        """
        return getToolByName(self.context, 'session_data_manager').getSessionData

    def event_datetime(self, item):
        """
        Returns datetime of event.

        1) When the start and end time are the same:
            Feb 25, 2013 12:00 AM

        2) When the start and end date are the same but not time:
            Feb 26, 2013 08:00 PM - 10:00 PM

        3) When the start and end date are different:
            Feb 27, 2013 12:00 AM - Feb 28, 2013 12:00 AM

        :param item: Instance
        :type item: plone.app.contentlisting.catalog.CatalogContentListingObject

        :rtype: unicode
        """
        start = item.start
        end = item.end
        start_dt = self.ulocalized_time(start, long_format=True, context=self.context)
        if start.Date() == end.Date():
            if start == end:
                dt = start_dt
            else:
                end_time = self.ulocalized_time(end, time_only=True)
                dt = u'{} - {}'.format(start_dt, end_time)
        else:
            end_dt = self.ulocalized_time(end, long_format=True, context=self.context)
            dt = u'{} - {}'.format(start_dt, end_dt)

        return dt

    @property
    @memoize
    def portal(self):
        """Returns portal object."""
        return getToolByName(self.context, 'portal_url').getPortalObject()

    @property
    @memoize
    def portal_path(self):
        """Returns portal path."""
        return '/'.join(self.portal.getPhysicalPath())
