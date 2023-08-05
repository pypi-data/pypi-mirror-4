from zope.i18nmessageid import MessageFactory
UserActionsPortletMessageFactory = MessageFactory('collective.portlet.userActionsPortlet')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
