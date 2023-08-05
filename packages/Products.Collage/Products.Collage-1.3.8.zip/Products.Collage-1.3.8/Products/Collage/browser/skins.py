# $Id$

from Products.Collage.utilities import CollageMessageFactory as _

class PortletDefaultSkin(object):
    title = _(u"default", default=u"Default")

class PortletNotificationSkin(object):
    title = _(u"notification_skin", default=u"Notification")

class PortletHelpSkin(object):
    title = _(u"help_skin", default=u"Help")
