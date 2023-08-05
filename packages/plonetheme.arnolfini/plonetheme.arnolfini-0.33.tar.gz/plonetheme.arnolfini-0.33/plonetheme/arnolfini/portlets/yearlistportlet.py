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
import time


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
        return self.isEventPast(self.context)
      
    def isEventPast(self, event):
        """
        Checks if the event is already past
        """
        if event.portal_type != 'Event' and event.portal_type != 'Media Event':
            return False
        else:
            return event.end() < time.time() 
    
    def css_class(self):
        return "portlet-yearListing"
    
    def getYears(self):
        """
        Get the year listing depending on the documented/undocumented events on the folder.
        """
    def getYears(self):
        """
        Get the year listing depending on the documented/undocumented events on the folder.
        """
        result = []
        now = date.today().year
        
        for year in range(1961, now+1):
            result.append(year)
        
        result.reverse();
        
        return result
    
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
                                 "sort_order": "reverse",
                                 "review_state": "published"})
        else:
            results = catalog.queryCatalog({"portal_type": "Media Event",
                                 "start": date_range_query,
                                 "sort_on": "start",
                                 "sort_order": "reverse",
                                 "review_state": "published",
                                 "hasMedia": True})
        
        return results
    
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

class AddForm(base.NullAddForm):
     """Portlet add form.
     """
     def create(self):
         return Assignment()
