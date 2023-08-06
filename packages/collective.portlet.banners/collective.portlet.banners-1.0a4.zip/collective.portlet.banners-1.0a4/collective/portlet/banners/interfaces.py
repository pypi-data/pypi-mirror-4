from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

class IPortletBanner(Interface):
    """
    A banner that can be displayed in the banner portlet
    """
    
class IBannersPortletLayer(IDefaultBrowserLayer):
    """
    Browser layer for the banners portlet.
    """