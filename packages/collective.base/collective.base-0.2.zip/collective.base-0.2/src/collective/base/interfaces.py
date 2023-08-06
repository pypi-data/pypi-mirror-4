from zope.interface import Attribute
from zope.interface import Interface


class IBaseAdapter(Interface):
    """Base interface for adapters"""

    def get_brains(interfaces=None, **query):  # pragma: no cover
        """Get brains."""

    def get_brain(interfaces=None, **query):  # pragma: no cover
        """Get brain which is supposed to be only one."""

    def get_object(interfaces=None, **query):  # pragma: no cover
        """Get object which is supposed to be only one."""

    def get_content_listing(interfaces=None, **query):  # pragma: no cover
        """Get ContentListing from brains gotten from get_brains method."""

    def event_datetime(item):  # pragma: no cover
        """Returns ulocalized_time event datetime."""

    catalog = Attribute("portal_catalog")
    ulocalized_time = Attribute("ulocalized_time method from translation_service")
    getSessionData = Attribute("getSessionData method from session_data_manager")
    context_path = Attribute("Path of the context")
    portal = Attribute("Portal object")
    portal_path = Attribute("Path of the portal")
