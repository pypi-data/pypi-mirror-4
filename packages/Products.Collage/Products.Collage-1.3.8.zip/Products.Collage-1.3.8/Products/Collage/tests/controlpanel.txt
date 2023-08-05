Control panel and global options
================================

We will check the options of the Collage control panel. First some settings.

    >>> from zope.component import getAdapter
    >>> from Products.Collage.utilities import getPortal
    >>> from Products.Collage.interfaces import ICollageSiteOptions
    >>> controlpanel = getAdapter(getPortal(), ICollageSiteOptions)
    >>> controlpanel
    <Products.Collage.browser.controlpanel.CollageSiteOptions object ...>

Checking default options
------------------------

    >>> controlpanel.use_whitelist
    False
    >>> len(controlpanel.types_whitelist)
    7
    >>> len(controlpanel.alias_whitelist)
    8

Any content type is enabled in a Collage.

    >>> 'Document' in controlpanel.types_whitelist
    True
    >>> controlpanel.enabledType('Document')
    True
    >>> controlpanel.enabledType('AnyOtherType')
    True
    >>> controlpanel.enabledAlias('Document')
    True
    >>> controlpanel.enabledAlias('AnyOtherType')
    True

Check enabled whitelist
-----------------------

    >>> controlpanel.use_whitelist = True
    >>> controlpanel.use_whitelist
    True

The ATDocument (as 7 other ATCT content types) is enabled.

    >>> controlpanel.enabledType('Document')
    True

    >>> controlpanel.enabledAlias('Document')
    True

When other content types are disabled.

    >>> controlpanel.enabledType('AnyOtherType')
    False

    >>> controlpanel.enabledAlias('AnyOtherType')
    False

Both lists behave different.

    >>> controlpanel.alias_whitelist = ('Event',)

    >>> controlpanel.enabledType('Document')
    True

    >>> controlpanel.enabledAlias('Document')
    False

    >>> controlpanel.enabledAlias('Event')
    True

