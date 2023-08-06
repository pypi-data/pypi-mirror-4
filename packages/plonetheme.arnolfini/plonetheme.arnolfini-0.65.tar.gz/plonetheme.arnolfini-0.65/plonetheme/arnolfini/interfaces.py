from zope.interface import Interface
from zope import schema
from plonetheme.arnolfini import MessageFactory as _

class IMediaTypes(Interface):
    """
    Marks all Media types from Products.media*
    """

class IWeekDayContent(Interface):
    """
    This interface defines the weekdays record on the registry
    """
    #form.fieldset(
     #   'Activate/deactivate', 
      #  label=_(u"Activate/deactivate"),
       # fields=['mondayActive', 'tuesdayActive', 'wednesdayActive', 'thursdayActive', 'fridayActive', 'saturdayActive', 'sundayActive']
    #)
    
    mondayActive = schema.Bool(
        title=_(u"monday_active", default=u"Active"),
        default=False,
        required=False)
    
    tuesdayActive = schema.Bool(
        title=_(u"tuesday_active", default=u"Active"),
        default=False,
        required=False)
    
    wednesdayActive = schema.Bool(
        title=_(u"wednesday_active", default=u"Active"),
        default=False,
        required=False)
    
    thursdayActive = schema.Bool(
        title=_(u"thursday_active", default=u"Active"),
        default=False,
        required=False)
    
    fridayActive = schema.Bool(
        title=_(u"friday_active", default=u"Active"),
        default=False,
        required=False)
    
    saturdayActive = schema.Bool(
        title=_(u"saturday_active", default=u"Active"),
        default=False,
        required=False)
    
    sundayActive = schema.Bool(
        title=_(u"sunday_active", default=u"Active"),
        default=False,
        required=False)
    
    monday = schema.Text(
        title=_(u"monday", default=u"Message"),
        description=_(u"monday_content", default=u"Content to display on Mondays."),
        default=u"",
        required=False)
    
    tuesday = schema.Text(
        title=_(u"tuesday", default=u"Message"),
        description=_(u"tuesday_content", default=u"Content to display on Tuesdays."),
        default=u"",
        required=False)
    
    wednesday = schema.Text(
        title=_(u"wednesday", default=u"Message"),
        description=_(u"wednesday_content", default=u"Content to display on Wednesdays."),
        default=u"",
        required=False)
    
    thursday = schema.Text(
        title=_(u"thursday", default=u"Message"),
        description=_(u"thursday_content", default=u"Content to display on Thursdays."),
        default=u"",
        required=False)
    
    friday = schema.Text(
        title=_(u"friday", default=u"Message"),
        description=_(u"friday_content", default=u"Content to display on Fridays."),
        default=u"",
        required=False)
    
    saturday = schema.Text(
        title=_(u"saturday", default=u"Message"),
        description=_(u"saturday_content", default=u"Content to display on Saturdays."),
        default=u"",
        required=False)
    
    sunday = schema.Text(
        title=_(u"sunday", default=u"Message"),
        description=_(u"sunday_content", default=u"Content to display on Sundays."),
        default=u"",
        required=False)
    
    no_event = schema.Text(
        title=_(u"no_event", default=u"No Events"),
        description=_(u"sunday_content", default=u"Content to display when there are no events."),
        default=u"",
        required=False)
    
    