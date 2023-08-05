from plone.app.search.browser import Search
from Products.Five import BrowserView
from plone.app.layout.viewlets.common import FooterViewlet
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from AccessControl import getSecurityManager
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.PloneBatch import Batch
from datetime import date
from DateTime import DateTime
from plone.app.querystring import queryparser
from collective.media.interfaces import ICanContainMedia
from collective.portlet.relateditems.relateditems import Renderer as RelatedItemsRenderer
from plone.portlet.collection.collection import Renderer as CollectionPortletRenderer
import re
import time
import json
from zope.component import getMultiAdapter
from Acquisition import aq_inner
from ZTUtils import make_query

try:
    from Products.PloneGetPaid.interfaces import IBuyableMarker
    GETPAID_EXISTS = True
except ImportError:
    GETPAID_EXISTS = False


class CommonBrowserView(BrowserView):
    """
    Common utilities for all the other views
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
        if hasattr(item, 'leadMedia'):
            lead = item.leadMedia
        else:
            catalog = getToolByName(self.context, 'portal_catalog')
            brains = catalog.queryCatalog({"UID": item.UID()})
            if len(brains) != 0:
                lead = brains[0].leadMedia
            else:
                lead = None
            
        if lead is not None:
                return '<img src="%(url)s" alt="%(title)s" title="%(title)s" />'%{'url': "%s/image_%s"%(lead, scale), 'title':item.Title}
        else:
            return ""
        
    def containsMedia(self, item):
        if hasattr(item, 'hasMedia'):
            return item.hasMedia
        else:
            catalog = getToolByName(self.context, 'portal_catalog')
            brains = catalog.queryCatalog({"UID": item.UID()})
            if len(brains) != 0:
                return brains[0].hasMedia
            else:
                return False
    
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
          
    def isEventPast(self, event):
        """
        Checks if the event is already past
        """
        if event.portal_type != 'Event' and event.portal_type != 'Media Event':
            return False
        else:
            return event.end() < time.time()
    
    def getCurrentTime(self):
        """
        Utility, returns a current DateTime object.
        """
        return DateTime()
    
    def getFormattedEventDate(self, event):
        """
        Formats the start and end dates properly and marks the event as past or future
        """
        if event.portal_type != 'Event' and event.portal_type != 'Media Event':
            return ""
        
        if event.start() is None or event.end() is None:
            if event.start() is None and event.end() is None:
                return ""
            else:
                samedate = True
        else:
            samedate = event.start().strftime('%d - %m - %Y') == event.end().strftime('%d - %m - %Y')
            
        finalDatesFmt = '<div class="dates %(class)s"><span class="dateText">%(dates)s%(hours)s</span></div>'
        
        dates = "%s"%(samedate and (event.start() is not None and event.start().strftime('%A, %d %B %Y') or event.end().strftime('%A, %d %B %Y')) or "%s to %s"%(event.start().strftime('%A, %d %B %Y'), event.end().strftime('%A, %d %B %Y')))
        
        openingHour = event.start() is not None and event.start().strftime('%H:%M') or "00:00"
        closingHour = event.end() is not None and event.end().strftime('%H:%M') or "00:00"
        hoursExist = openingHour != closingHour
        
        hours = hoursExist and ', <span class="hours">%s to %s</span>'%(openingHour, closingHour) or ''
        
        finalDates = finalDatesFmt%{'class': self.isEventPast(event) and 'past' or 'future', 'dates': dates, 'hours': hours}
        
        return finalDates
            
    def isBuyable(self, item):
        """
        Check if an item is buyable with PloneGetPaid
        """
        if not GETPAID_EXISTS:
            return False
        else:
            return IBuyableMarker.providedBy(item)
    
    def getEventBookingLink(self, event):
        """
        Check if the booking information is a link or just a code. return a full url
        """
        if not event.getBooking():
            return ""
        else:
            if event.getLink().find("http://") != -1:
                return event.getLink()
            else:
                return 'http://purchase.tickets.com/buy/TicketPurchase?agency=ARNOLFINI&organ_val=26385&schedule=list&event_val=%s'%event.getLink()
      
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
    def results(self, batch=True, b_start = 0, pagesize=10, only_documented=False):
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
            if batch:
               results = Batch(final_res, pagesize, start=b_start)
            else:
                return final_res
        elif self.context.portal_type  == 'Folder':
            brains = self.context.getFolderContents()
            if only_documented:
                final_res = []
                for res in brains:
                    if res.hasMedia:
                        final_res.append(res)
            else:
                final_res = list(brains)
            if batch:
                results = Batch(final_res, pagesize, start=b_start)
            else:
                return final_res
            
        return results
    
    def sort_by_alpha(self, results, field):
        """
        Sorts results by field in alphabetic order
        """
        res_list = list(results)
        final_res = sorted(res_list, key=lambda x: getattr(x, field, False))
        
        return Batch(final_res, results.size, start=results.start)
  
class EventListingView(FolderListing):
    """'
    Event listing view class.
    """
    cachedResults = None
    
    def resultsToday(self, only_documented=False):
        """
        returns a result list for events that: start <= today <= end;  Reverse chronological order
        """
        #Cache results layzily for better performance
        if self.cachedResults is None:
            self.cachedResults = self.results(batch=False, only_documented=only_documented)
        
        res_list = []
        today = DateTime()
        
        for res in self.cachedResults:
            if res.start <= today and today <= res.end:
                res_list.append(res)
        
        final_res = sorted(res_list, key=lambda x: getattr(x, "start", False), reverse=True)
        
        return final_res
        
    def resultsFuture(self , only_documented=False):
        """
        returns a result list for events that: today < start; Chronological order
        """
        #Cache results layzily for better performance
         #Cache results layzily for better performance
        if self.cachedResults is None:
            self.cachedResults = self.results(batch=False, only_documented=only_documented)
        
        res_list = []
        today = DateTime()
        
        for res in self.cachedResults:
            if today < res.start:
                res_list.append(res)
        
        #NOTE: No need to sort here since the collection is already ordered that way but it might be mor powerfull to sort anyway... for now leaving it like this for performance sake
        #final_res = sorted(res_list, key=lambda x: getattr(x, "start", False))
        
        return res_list
        
        
    
class SearchView(CommonBrowserView, Search):
    """
    Adding to Search view
    """
    
class NumberOfResults(CommonBrowserView):
    """
    Called by AJAX to know how many results in the collection. Returns JSON.
    """
    def getJSON(self):
        callback = hasattr(self.request, 'callback') and 'json' + self.request['callback'] or None
        only_documented = not hasattr(self.request, 'only_documented') 
        
        result = None
        
        if self.context.portal_type == 'Collection':
            brains = self.context.queryCatalog(batch=False)
            if only_documented:
                result = []
                for res in brains:
                    if res.hasMedia:
                        result.append(res)
    
        if result is not None:
            jsonStr = json.dumps(len(result))
        else:
            jsonStr = json.dumps(result)
            
        if callback is not None:
            return callback +'(' + jsonStr + ')'
        else:
            return jsonStr 


class BlogView(FolderListing):
    """
    Adding to Blog view
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
        
class TitleViewlet(ViewletBase):
    """
    Changing the title format
    """
    index = ViewPageTemplateFile('title.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        context_state = getMultiAdapter((self.context, self.request),
                                         name=u'plone_context_state')
        page_title = escape(safe_unicode(context_state.object_title()))
        portal_title = escape(safe_unicode(portal_state.navigation_root_title()))
        if page_title == portal_title:
            self.site_title = portal_title
        else:
            self.site_title = u"%s &larr; %s" % (page_title, portal_title)


class RelatedItems(RelatedItemsRenderer, CommonBrowserView):
    """
    Overriding the related Items
    """
    _template = ViewPageTemplateFile('relateditems.pt')
    
    
    def getAllRelatedItemsLink(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal_url = portal_state.portal_url()
        context = aq_inner(self.context)
        req_items = {}
        # make_query renders tuples literally, so let's make it a list
        req_items['Subject'] = list(context.Subject())
        if not self.data.show_all_types:
            req_items['portal_type'] = list(self.data.allowed_types)
        return '%s/@@search?%s' % (portal_url, make_query(req_items))
    
    
class CollectionPortlet(CollectionPortletRenderer, CommonBrowserView):
    """
    Overriding the related Items
    """
    _template = ViewPageTemplateFile('collection.pt')
    render = _template

class FrontPageView(FolderListing):
    """
    View for the collection in the front page, it has a top section that has a main item of content (later it will be a slideshow)
    and two portlet managers
    """
    def getMainContent(self):
        """
        This function returns the first item of the chosen collection.
        """
        collection = self.context.restrictedTraverse("/arnolfini/front-page-main")
        results = collection.queryCatalog()
        
        if len(results) > 0:
            return results[0]
        else:
            return None
        
    def showManageButton(self):
        secman = getSecurityManager()
        if not secman.checkPermission('Portlets: Manage portlets', self.context):
            return False
        else:
            return True