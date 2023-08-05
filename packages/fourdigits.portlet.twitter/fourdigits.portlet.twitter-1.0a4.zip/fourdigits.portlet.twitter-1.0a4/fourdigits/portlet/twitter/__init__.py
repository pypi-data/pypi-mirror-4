from zope.i18nmessageid import MessageFactory
name = 'fourdigits.portlet.twitter'
FourdigitsPortletTwitterMessageFactory = MessageFactory(name)

from Products.CMFCore.permissions import setDefaultRoles
setDefaultRoles('fourdigits.portlet.twitter: Add FourdigitsPortletTwitter',
                ('Manager', 'Site Administrator', 'Owner',))

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
