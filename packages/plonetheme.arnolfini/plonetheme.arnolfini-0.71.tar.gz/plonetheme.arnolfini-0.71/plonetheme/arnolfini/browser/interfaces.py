from plonetheme.intkBase.browser.interfaces import IIntkBaseLayer
from plone.theme.interfaces import IDefaultPloneLayer
from plone.portlets.interfaces import IPortletManager
from plone.app.portlets.interfaces import IColumn
from zope.viewlet.interfaces import IViewletManager

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
       If you need to register a viewlet only for the
       "Arnolfini Theme" theme, this interface must be its layer
       (in arnolfini/viewlets/configure.zcml).
    """

class IFrontPagePortletManagerLeft(IPortletManager, IColumn):
    """The first front page view portlet """
    
class IFrontPagePortletManagerRight(IPortletManager, IColumn):
    """The second front page view portlet """

class ICarouselManager(IViewletManager):
    """ A Viewlet manager for the portlet view to add the carousel on."""