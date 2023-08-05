from zope.i18nmessageid import MessageFactory
NavigationExtendedPortletMessageFactory = MessageFactory('collective.portlet.sitemap')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
