# -*- coding: utf-8 -*-
# $Id$
"""Collage config constants"""

PROJECTNAME = "Collage"
I18N_DOMAIN = PROJECTNAME.lower()
PROPERTYSHEETNAME = 'collage_properties'
COLLAGE_TYPES = ('Collage', 'CollageRow', 'CollageColumn', 'CollageAlias')

from Products.CMFCore.permissions import setDefaultRoles

DEFAULT_ADD_CONTENT_PERMISSION = "Add Collage content"
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner', 'Contributor'))

import os
PACKAGE_HOME = os.path.dirname(os.path.abspath(__file__))
del os
