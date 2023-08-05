from plone.app.search.browser import Search
from Products.Five import BrowserView
from plone.app.layout.viewlets.common import FooterViewlet
from AccessControl import getSecurityManager

class CommonBrowserView(BrowserView):
    """
    Common utilities for all the other views
    """

class DocumentView(CommonBrowserView):
    """'
    Override of document view class.
    """
    
class EventView(CommonBrowserView):
    """'
     Override of media event view class.
    """
    
class FolderListing(CommonBrowserView):
    """'
    Override of folder_listing view
    """
    
class SearchView(Search):
    """
    Adding to Search view
    """

class Footer(FooterViewlet):
    """
    helper classes for footer
    """
    def showManageButton(self):
        secman = getSecurityManager()
        if not secman.checkPermission('Portlets: Manage portlets', self.context):
            return False
        else:
            return True