# -*- coding: utf-8 -*-
# $Id$
"""Misc GenericSetup upgrade steps"""

# Warning, the various upgrade handlers here must be coded in
# a defensive way. This means that the changes each handler does
# may have already done. The handler must behave accordingly.

from Products.Collage.utilities import getPortal, IfInstalled

PROFILE_NAME = 'profile-Products.Collage:default'

safety_belt = IfInstalled()

@safety_belt
def runTypesStepOnly(setuptool):
    """We upgrade our types only
    """
    setuptool.runImportStepFromProfile(PROFILE_NAME, 'typeinfo', run_dependencies=True)
    return


@safety_belt
def updateJSRegistry(setuptool):
    """Javascript moved from skins to resources
    """
    OLDID = 'collage.js'
    NEWID = '++resource++collage-resources/collage.js'
    jstool = getPortal().portal_javascripts
    all_rscids = jstool.getResourceIds()
    if (OLDID in all_rscids) and (NEWID not in all_rscids):
        jstool.renameResource(OLDID, NEWID)
    return


@safety_belt
def removeSkinsLayer(setuptool):
    """Collage doesn't require a CMF skins layer anymore
    """
    LAYERNAME = 'Collage'
    skinstool = getPortal().portal_skins
    # Unfortunately, there's no easy way to remove a layer from all skins

    skinnames = skinstool.selections.keys()
    for name in skinnames:
        layers = skinstool.selections[name]
        layers = [l.strip() for l in layers.split(',')
                  if l.strip() != LAYERNAME]
        layers = ','.join(layers)
        skinstool.selections[name] = layers
    if LAYERNAME in skinstool.objectIds():
        skinstool._delObject(LAYERNAME)
    return


@safety_belt
def addControlPanel(setuptool):
    """Add Collage control panel resources
    """
    for step in ('propertiestool', 'controlpanel', 'action-icons'):
        setuptool.runImportStepFromProfile(PROFILE_NAME, step, run_dependencies=False)
    return


@safety_belt
def addAliasWhitelistProperty(setuptool):
    """Add Alias whitelist control panel property
    """
    propsheet = getPortal().portal_properties.collage_properties
    # Default: same value as types whitelist
    default_value = propsheet.getProperty('types_whitelist')
    if propsheet.getProperty('alias_whitelist'):
        # property already exists; upgrade step has already been run
        # apparently; upgrade steps should not fail when run a second
        # time, so we return here.
        return
    propsheet.manage_addProperty('alias_whitelist', default_value, 'lines')
    return


@safety_belt
def upgradeTo1_3_0(setuptool):
    """Lots of changes in setup in 1.3.0
    """
    # We must delete ftis since something whoes in the 'typeinfo' step
    # FIXME: is this a GS bug or feature?
    portal_types = getPortal().portal_types
    for portal_type in ('Collage', 'CollageRow', 'CollageColumn', 'CollageAlias'):
        portal_types._delObject(portal_type)

    for step in ('typeinfo', 'cssregistry', 'actions', 'action-icons', 'jsregistry'):
        setuptool.runImportStepFromProfile(PROFILE_NAME, step, run_dependencies=False)

    # Remove useless alias_search_limit option in property sheet
    to_delete = 'alias_search_limit'
    propsheet = getPortal().portal_properties.collage_properties
    if propsheet.hasProperty(to_delete):
        propsheet._delProperty(to_delete)

    # Adding new properties
    to_add = [
        # Name, value, type
        ('ref_browser_empty', False, 'boolean'),
        ('ref_browser_types', False, 'boolean'),
        ('batch_size', 3, 'int')
        ]
    for name, value, ptype in to_add:
        if propsheet.hasProperty(name):
            continue
        propsheet.manage_addProperty(name, value, ptype)
    return

