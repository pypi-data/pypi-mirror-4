from plone.app.search.browser import Search
from Products.Five import BrowserView
from plone.app.layout.viewlets.common import FooterViewlet
from AccessControl import getSecurityManager
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from datetime import date
from DateTime import DateTime
from plone.app.querystring import queryparser
import re


class CommonBrowserView(BrowserView):
    """
    Common utilities for all the other views
    """
    def slideshow(self, parent):
        """
        Creates a slideshow with the media from parent
        """
        parentURL = parent.absolute_url()
        structure = """
        <div class="embededMediaShow">
            <a  href="%s?recursive=true">slideshow</a>
        </div>
        """%parentURL
        
        return structure
    
    def getLeadMediaTag(self, item, scale="large"):
        lead = item.leadMedia
        if lead is not None:
            return '<img src="%(url)s" alt="%(title)s" title="%(title)s" />'%{'url': "%s/image_%s"%(lead, scale), 'title':item.Title}
    
    def trimText(self, text, limit, strip=False):
        if strip:
            text = self.stripTags(text)
    
        if len(text) > limit: 
            res = text[0:limit]
            lastspace = res.rfind(" ")
            res = res[0:lastspace] + " ..."
            return res
        else:
            return text
            
    def stripTags(self, text):
        return re.sub('<[^<]+?>', '', text)
    
    def getTwoWayRelatedContent(self):
        """
        Gets all the manually related content both related items of the current context and items where the current context is marked as related.
        """
        related = []
        related = self.context.getRefs()
        backRelated = self.context.getBRefs()
        
        related.extend(backRelated)
        
        return self._uniq(related);
        
    def getContentAsLinks(self, content):
        """
        A commodity, this formats a content list content as an HTML structure of titles with links. Comma separated. Used to list the artists related to an exhibition.
        """
        result = []
        for res in content:
            if res.portal_type == 'Media Person':
                result.append('<a href="%(link)s">%(title)s</a>'%{'link':res.absolute_url(), 'title':self._normalizePersonName(res.title)})
            else:
                result.append('<a href="%(link)s">%(title)s</a>'%{'link':res.absolute_url(), 'title':res.title})               
        
        return ", ".join(result)
    
    def getTwoWayRelatedContentOfType(self, typeList):
        result = []
        for res in self.getTwoWayRelatedContent():
            if res.portal_type in typeList:
                result.append(res)
                
        return result
    
    def _normalizePersonName(self, person):
        names = person.split(",")
        if len(names) == 2:
            return "%s %s"%(names[1], names[0])
        else:
            return person
            
    def _uniq(self, alist):    # Fastest order preserving
        set = {}
        return [set.setdefault(e,e) for e in alist if e not in set]
        
class DocumentView(CommonBrowserView):
    """'
    Override of document view class.
    """
    
class EventView(CommonBrowserView):
    """'
     Override of media event view class.
    """
    nxt = None
    prv = None
    
    def cacheNextPrev(self):
        """
        Caches the values for next and prev
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog.queryCatalog({"portal_type": "Media Event",
                                 "sort_on": "start",
                                 "hasMedia": True,
                                 "review_state": "published"})
        
        for i in range(0, len(results)):
            if results[i].UID == self.context.UID():
                if i < len(results) - 2:
                    self.nxt = results[i +1]
    
                if i > 0:
                    self.prv = results[i -1]
    
    def getNextEvent(self):
        """
        Gets the next event in chronological order.
        """
        if self.nxt is None:
            self.cacheNextPrev()
        
        return self.nxt
    
    def getPrevEvent(self):
        """
        Gets the previous event in chronological order
        """
        if self.prv is None:
            self.cacheNextPrev()
        
        return self.prv
        
    
class EventArchiveView(EventView):
    """'
    Event archive view class.
    """
    
class EventArchiveListingView(CommonBrowserView):
    """'
    Event archive view class.
    """
    def results(self, b_start = 0, pagesize=10):
        all_results = self.context.queryCatalog(batch=False)
        final_res = []
        for res in all_results:
            if self.yearIsDocumented(res.id):
                final_res.append(res)
        return Batch(final_res, pagesize, start=b_start)
    
    def innerResults(self, item, limit=3):
        #TODO: If we can query specifically for the hasMedia then we don't need to bypass the batching anymore
        all_results = item.getObject().queryCatalog(batch=False)
        
        final_res = []
        
        for res in all_results:
            if self.eventIsDocumented(res):
                final_res.append(res)
        return Batch(final_res, limit)
    
    def getEventsForYear(self, year, only_documented=False):
        """
        Get the documented/undocumented events for the specific year.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        
        start = DateTime(year,1,1)
        end = DateTime(year,12,31) 
        date_range_query = {'query': (start, end), 'range': 'min:max'}

        if not only_documented:
            results = catalog.queryCatalog({"portal_type": "Media Event",
                                 "start": date_range_query,
                                 "sort_on": "start",
                                 "review_state": "published"})
        else:
            results = catalog.queryCatalog({"portal_type": "Media Event",
                                 "start": date_range_query,
                                 "sort_on": "start",
                                 "review_state": "published",
                                 "hasMedia": True})
            
        return results
    
    def yearIsDocumented(self, year):
        """
        Checks if a year has any documented events
        """
        try:
            int(year)
        except:
            return False
        
        events = self.getEventsForYear(int(year))
        
        if len(events) == 0:
            return False
        
        if self._showall():
            return True
        
        #go through events until we find one that has docs.
        for event in events:
            if self.eventIsDocumented(event):
                return True
        
        return False
    
    def eventIsDocumented(self, event):
        """
        Check if the event has media documentation
        """  
        if self._showall():
            return True
        else:
            return event.hasMedia
        
    def _showall(self):
        return self.request.get('showallyears', False)

class FolderListing(CommonBrowserView):
    """'
    Override of folder_listing view
    """
    def results(self, b_start = 0, pagesize=10, only_documented=False):
        results = []
        
        if self.context.portal_type  == 'Collection':
            brains = self.context.queryCatalog(batch=False)
            if only_documented:
                final_res = []
                for res in brains:
                    if res.hasMedia:
                        final_res.append(res)
            else:
                final_res = list(brains)
            results = Batch(final_res, pagesize, start=b_start)
        elif self.context.portal_type  == 'Folder':
            brains = self.context.getFolderContents()
            if only_documented:
                final_res = []
                for res in brains:
                    if res.hasMedia:
                        final_res.append(res)
            else:
                final_res = list(brains)
            results = Batch(final_res, pagesize, start=b_start)
            
        return results
    
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