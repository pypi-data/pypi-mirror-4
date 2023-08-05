import random

from AccessControl import getSecurityManager

from zope.interface import implements
from zope.component import getMultiAdapter, getUtility

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form

from plone.memoize.instance import memoize

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget

from plone.i18n.normalizer.interfaces import IIDNormalizer

from Products.CMFCore.utils import getToolByName
from datetime import date
from DateTime import DateTime


class IYearListPortlet(IPortletDataProvider):
    """A portlet which renders the author of the current object
    """


class Assignment(base.Assignment):
    """
    Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IYearListPortlet)

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return "Year Listing Portlet"


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('yearlistingportlet.pt')
    render = _template

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    @property
    def available(self):
        return not self.context.restrictedTraverse('@@plone_context_state').is_view_template()
       
    
    def css_class(self):
        return "portlet-yearListing"
    
    def getYears(self):
        """
        Get the year listing depending on the documented/undocumented events on the folder.
        """
        result = []
        now = date.today().year
        if self.context.portal_type == "Media Event":
            prevYear = 0
            nextYear = 0
            currentYear = self.context.start().year()
            prevYear = currentYear - 1
            nextYear = currentYear +1
            
            while not self._yearIsDocumented(prevYear) and prevYear > 1900:
                prevYear = prevYear - 1
                
            while not self._yearIsDocumented(nextYear) and nextYear < 2020:
                nextYear = nextYear + 1
            
            if prevYear > 1900:
                result.append(prevYear)
                
            result.append(currentYear)
            
            if nextYear < 2020:
                result.append(nextYear)
            
        else:
            #TODO: handle other types such as folers and collections. In this case show all  available years
            pass
        
        return result
    
    def getEventsForYear(self, year, only_documented=False):
        """
        Get the documented/undocumented events for the specific year.
        """
        catalog = getToolByName(self.context, 'portal_catalog')
        
        start = DateTime(year,1,1)
        end = DateTime(year,12,31) 
        date_range_query = {'query': (start, end), 'range': 'min:max'}

        results = catalog.queryCatalog({"portal_type": "Media Event",
                                 "start": date_range_query,
                                 "sort_on": "start",
                                 "sort_order": "reverse",
                                 "review_state": "published"})
        
        if not only_documented:
            return results
        else:
            filtered = []
            for event in results:
                if self._eventIsDocumented(event):
                    filtered.append(event)
            return filtered
    
    def isCurrentYear(self, year):
        """
        Check if year is the current context year
        """
        result = False
        if self.context.portal_type == "Media Event":
            currentYear = self.context.start().year()
            result = currentYear == year
        else:
            #TODO: handle other types such as folers and collections. if it's one of  the "year collections" make the check if not just let it return false
            pass
        
        return result
    
    def clip(self, desc, num):
        if len(desc) > num:
            res = desc[0:num]
            lastspace = res.rfind(" ")
            res = res[0:lastspace] + " ..."
            return res
        else:
            return desc

    def _yearIsDocumented(self, year):
        """
        Checks if a year has any documented events
        """
        #TODO: This check will make the website slow... this should be encapsulated and optimized. should be done on collective.media instead.
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
            if self._eventIsDocumented(event):
                return True
        
        return False

    def _eventIsDocumented(self, event):
        """
        Check if the event has media documentation
        """
        if self._showall():
            return True
        else:
            #TODO: collective.media function hasMedia() hardcoded here. This fucking sucks!!
            #event.hasMedia()
            item = event
            results = []
            
            catalog = getToolByName(self.context, 'portal_catalog')
            plone_utils = getToolByName(self.context, 'plone_utils')
            path = item.getPath() + "/"
            
            if item.portal_type == "Folder" or (item.restrictedTraverse('@@plone').isStructuralFolder()  and item.portal_type != "Topic"):
                results = catalog.searchResults(path = {'query' : path}, type = ['Image', 'Link'], sort_on = 'getObjPositionInParent')
            elif item.portal_type == "Topic":
                if item.limitNumber:
                    results = catalog.searchResults(item.buildQuery())[:item.itemCount]
                else:
                    results = catalog.searchResults(item.buildQuery())
            
            resultArray = []
            
            for res in results:
                if res.portal_type == "Image":
                    resultArray.append(res)
                #TODO: Somehow res has no remoteUrl. Could it be a brain vs. object thing?
                #elif res.portal_type == "Link" and (res.remoteUrl.find("youtube.com") > -1 or res.remoteUrl.find("vimeo.com") > -1):
                #    resultArray.append(res)
            
            return len(resultArray) > 0
    
    def _showall(self):
        return self.request.get('showallyears', False)

class AddForm(base.NullAddForm):
     """Portlet add form.
     """
     def create(self):
         return Assignment()
