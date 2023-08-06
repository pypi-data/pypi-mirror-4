# -*- extra stuff goes here -*-

from zope.i18nmessageid import MessageFactory

pageHeaderMF = MessageFactory('collective.pageheader')

_ = pageHeaderMF


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
