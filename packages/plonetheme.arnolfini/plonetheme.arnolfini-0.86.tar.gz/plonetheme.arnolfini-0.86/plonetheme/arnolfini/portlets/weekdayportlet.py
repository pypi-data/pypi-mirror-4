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
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget

from plone.i18n.normalizer.interfaces import IIDNormalizer

from Products.CMFCore.utils import getToolByName
from datetime import date
from DateTime import DateTime
import time

from plonetheme.arnolfini import MessageFactory as _

from Acquisition import aq_inner


class IWeekDayPortlet(IPortletDataProvider):
    """A portlet which renders content depending on the day of the week
    """
    header = schema.TextLine(
        title=_(u"title", default=u"Title"),
        description=_(u"portlet_title", default=u"Title of the portlet. Leave empty to display the current date."),
        default=u"",
        required=False)
    
    monday = schema.Text(
        title=_(u"monday", default=u"Monday"),
        description=_(u"monday_content", default=u"Content to display on Mondays"),
        default=u"",
        required=False)
    
    tuesday = schema.Text(
        title=_(u"tuesday", default=u"Tuesday"),
        description=_(u"tuesday_content", default=u"Content to display on Tuesdays"),
        default=u"",
        required=False)
    
    wednesday = schema.Text(
        title=_(u"wednesday", default=u"Wednesday"),
        description=_(u"wednesday_content", default=u"Content to display on Wednesdays"),
        default=u"",
        required=False)
    
    thursday = schema.Text(
        title=_(u"thursday", default=u"Thursday"),
        description=_(u"thursday_content", default=u"Content to display on Thursdays"),
        default=u"",
        required=False)
    
    friday = schema.Text(
        title=_(u"friday", default=u"Friday"),
        description=_(u"friday_content", default=u"Content to display on Fridays"),
        default=u"",
        required=False)
    
    saturday = schema.Text(
        title=_(u"saturday", default=u"Saturday"),
        description=_(u"saturday_content", default=u"Content to display on Saturdays"),
        default=u"",
        required=False)
    
    sunday = schema.Text(
        title=_(u"sunday", default=u"Sunday"),
        description=_(u"sunday_content", default=u"Content to display on Sundays"),
        default=u"",
        required=False)

class Assignment(base.Assignment):
    """
    Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    implements(IWeekDayPortlet)
    
    header = u''
    monday = u'' 
    tuesday = u''
    wednesday = u''
    thursday = u''
    friday = u''
    saturday = u''
    sunday = u''
    
    def __init__(self, header = u'', monday = u'', tuesday = u'', wednesday = u'', thursday = u'', friday = u'', saturday = u'', sunday = u''):
        self.header = header
        self.monday = monday
        self.tuesday = tuesday
        self.wednesday = wednesday
        self.thursday = thursday
        self.friday = friday
        self.saturday = saturday
        self.sunday = sunday
        
        
    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave or
        static string if title not defined.
        """
        return self.header or _(u'weekday_portlet', default=u"Weekday Portlet")

class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('weekdayportlet.pt')
    render = _template

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    @property
    def available(self):
        return True
    
    def css_class(self):
        return "portlet-weekday"
    
    def getTitle(self):
        if self.data.header:
            return self.data.header
        else:
            return DateTime().strftime("%A %d %B %Y")
    
    def getTodayContent(self):
        weekday = DateTime().strftime("%u")
        if weekday == '1':
            return self.transformed(self.data.monday)
        elif weekday == '2':
            return self.transformed(self.data.tuesday)
        elif weekday == '3':
            return self.transformed(self.data.wednesday)
        elif weekday == '4':
            return self.transformed(self.data.thursday)
        elif weekday == '5':
            return self.transformed(self.data.friday)
        elif weekday == '6':
            return self.transformed(self.data.saturday)
        elif weekday == '7':
            return self.transformed(self.data.sunday)
        
    def transformed(self, text, mt='text/x-html-safe'):
        """Use the safe_html transform to protect text output. This also
            ensures that resolve UID links are transformed into real links.
        """
        orig = text
        context = aq_inner(self.context)
        if not isinstance(orig, unicode):
            # Apply a potentially lossy transformation, and hope we stored
            # utf-8 text. There were bugs in earlier versions of this portlet
            # which stored text directly as sent by the browser, which could
            # be any encoding in the world.
            orig = unicode(orig, 'utf-8', 'ignore')
            logger.warn("Static portlet at %s has stored non-unicode text. "
                "Assuming utf-8 encoding." % context.absolute_url())

        # Portal transforms needs encoded strings
        orig = orig.encode('utf-8')

        transformer = getToolByName(context, 'portal_transforms')
        data = transformer.convertTo(mt, orig,
                                     context=context, mimetype='text/html')
        result = data.getData()
        if result:
            if isinstance(result, str):
                return unicode(result, 'utf-8')
            return result
        return None

class AddForm(base.AddForm):
    form_fields = form.Fields(IWeekDayPortlet)
    form_fields['monday'].custom_widget = WYSIWYGWidget
    form_fields['tuesday'].custom_widget = WYSIWYGWidget
    form_fields['wednesday'].custom_widget = WYSIWYGWidget
    form_fields['thursday'].custom_widget = WYSIWYGWidget
    form_fields['friday'].custom_widget = WYSIWYGWidget
    form_fields['saturday'].custom_widget = WYSIWYGWidget
    form_fields['sunday'].custom_widget = WYSIWYGWidget
    label = _(u"Add week day portlet")
    description = _(u"This portlet renders content depending on the day of the week.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(IWeekDayPortlet)
    form_fields['monday'].custom_widget = WYSIWYGWidget
    form_fields['tuesday'].custom_widget = WYSIWYGWidget
    form_fields['wednesday'].custom_widget = WYSIWYGWidget
    form_fields['thursday'].custom_widget = WYSIWYGWidget
    form_fields['friday'].custom_widget = WYSIWYGWidget
    form_fields['saturday'].custom_widget = WYSIWYGWidget
    form_fields['sunday'].custom_widget = WYSIWYGWidget
    label = _(u"Edit week day portlet")
    description = _(u"This portlet renders content depending on the day of the week.")


