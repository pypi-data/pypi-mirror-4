from zope.i18nmessageid import MessageFactory
_ = MessageFactory('raptus.notification')

from Products.CMFCore.permissions import setDefaultRoles

ADD_PORTLET_PERMISSION = "raptus.notification: Add notification portlet"

setDefaultRoles(ADD_PORTLET_PERMISSION, ('Manager', 'Site Administrator',))
