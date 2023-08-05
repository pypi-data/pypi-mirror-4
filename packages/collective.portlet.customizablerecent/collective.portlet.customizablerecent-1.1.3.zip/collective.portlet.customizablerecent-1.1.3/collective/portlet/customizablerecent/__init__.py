from zope.i18nmessageid import MessageFactory
CustomizableRecentMessageFactory = MessageFactory('collective.portlet.customizablerecent')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
