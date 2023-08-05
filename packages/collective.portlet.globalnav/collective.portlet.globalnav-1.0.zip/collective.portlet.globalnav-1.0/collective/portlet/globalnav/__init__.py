from zope.i18nmessageid import MessageFactory
GlobalNavigationPortletMessageFactory = MessageFactory('collective.portlet.globalnav')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
