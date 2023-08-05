# -*- coding: utf-8 -*-
# $Id$

from zope import interface
from zope import schema
from zope.viewlet.interfaces import IViewletManager
from zope.i18nmessageid import MessageFactory
from Products.Collage.config import I18N_DOMAIN

_ = MessageFactory(I18N_DOMAIN)

class ICollage(interface.Interface):
    pass

class ICollageRow(interface.Interface):
    pass

class ICollageColumn(interface.Interface):
    pass

class ICollageAlias(interface.Interface):
    pass

class IDynamicViewManager(interface.Interface):
    pass

class ICollageBrowserLayer(interface.Interface):
    """Collage browser layer. Views registered with this layer
    are available to objects inside a collage."""
    pass

class ICollageBrowserLayerType(interface.interfaces.IInterface):
    """Marker interface for Collage theme-specific layers
    """
    pass

class ICollageEditLayer(interface.Interface):
    """Collage edit layer."""
    pass

class IContentMenu(IViewletManager):
    """Interface for the content-menu viewlet manager."""
    pass

class IPortletSkin(interface.Interface):
    """Interface for skinable portlets views."""
    pass

class ICollageSiteOptions(interface.Interface):

    ref_browser_empty = schema.Bool(
        title=_(u'label_ref_browser_empty',
                default=u"Open reference Browser without initial item listing"),
        description=_(u'help_ref_browser_empty',
                      default=u"Use this if you have lots of items in your "
                              u"containers."),
        default=False,
        required=True)

    ref_browser_types = schema.Bool(
        title=_(u'label_ref_browser_types',
                default=u"Provide type filter in reference browser"),
        description=_(u'help_ref_browser_types',
                      default=u"When set to True, the reference browser shows "
                              u"up a content type filter."),
        default=False,
        required=True)

    use_whitelist = schema.Bool(
        title=_(u'label_use_whitelist', default=u"Use types whitelist"),
        description=_(u'help_use_whitelist',
                      default=u"Only types in below whitelist can be added in "
                            u"a Collage."),
        default=False,
        required=True)

    types_whitelist = schema.Tuple(
        title=_(u'label_types_whitelist', default=u"Types whitelist"),
        description=_(u'help_types_whitelist',
                      default=u"Select item types that can be added in a "
                              u"Collage object."),
        required=False,
        missing_value=tuple(),
        value_type=schema.Choice(
            vocabulary='collage.vocabularies.CollageUserFriendlyTypes')
        )

    alias_whitelist = schema.Tuple(
        title=_(u'label_alias_whitelist', default=u"Alias whitelist"),
        description=_(u'help_alias_whitelist',
                      default=u"Select item types that can be aliased in a "
                            u"Collage object."),
        required=False,
        missing_value=tuple(),
        value_type=schema.Choice(
            vocabulary='collage.vocabularies.CollageUserFriendlyTypes')
        )

    batch_size = schema.Int(
        title=_(u'label_batch_size', default=u"Number of Columns"),
        description=_(u'help_batch_size',
            default=u"If the number of Columns in a row exceeds this number, "
                """"Collage will put these in a new "batch". """
                "The new batch will be displayed below the first batch, "
                "but it's technically still the same row. "),
        required=False,
        default=3,
        )

    def enabledType(portal_type):
        """True if portal type is enabled for adding in a Collage."""

    def enabledAlias(portal_type):
        """True if portal type is enabled for alias in a Collage"""
