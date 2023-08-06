#
#    Copyright 2010-2012 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#

#
# This is our shim layer to protect us from all the evils and clunkers in Zenoss
#
from AccessControl.class_init import InitializeClass
from AccessControl.Permissions import manage_properties
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
from OFS.PropertyManager import PropertyManager

from Products.ZenModel.ZenModelBase import ZenModelBase
from Products.ZenRelations.ZenPropertyManager import ZenPropertyManager


class PortalContent(ZenPropertyManager, ZenModelBase, SimpleItem):
    """
    the simplist type of content that supports FTI in Zenoss
    """

    __ac_permissions__ = ZenPropertyManager.__ac_permissions__ + (
        (manage_properties, ('getMenuIds',)),
        ) + ZenModelBase.__ac_permissions__ + SimpleItem.__ac_permissions__

    manage_options = ZenPropertyManager.manage_options + SimpleItem.manage_options

    def zenPropertyIds(self, *args, **kw):
        """
        """
        return PropertyManager.propertyIds(self)

    def getZenRootNode(self):
        """Return the root node for our zProperties."""
        return self.getDmdRoot(self.dmdRootName)

    def getMenuIds(self):
        """
        our helper to supply menus for edit form

        the standard is to create menu's with the ZenPack name ...
        """
        return ()

    def breadCrumbs(self):
        """
        seems crumbs get dropped off ...
        """
        crumbs = ZenModelBase.breadCrumbs(self)

        if crumbs[-1][1] != self.getId():
            crumbs.append((self.absolute_url(1), self.getId()))

        return crumbs

InitializeClass(PortalContent)


class PortalFolder(Folder, PortalContent):
    """
    A container type
    """
    __ac_permissions__ = Folder.__ac_permissions__ + PortalContent.__ac_permissions__

InitializeClass(PortalFolder)


