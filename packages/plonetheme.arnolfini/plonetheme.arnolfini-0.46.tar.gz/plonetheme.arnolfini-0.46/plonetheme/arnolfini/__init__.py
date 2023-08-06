  # -*- extra stuff goes here -*- 
from zope.i18nmessageid import MessageFactory as BaseMessageFactory

MessageFactory = BaseMessageFactory('plonetheme.arnolfini')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

