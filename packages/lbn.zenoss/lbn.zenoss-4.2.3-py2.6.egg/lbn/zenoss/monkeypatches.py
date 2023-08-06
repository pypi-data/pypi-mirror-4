#
# Copyright 2010-2013 Corporation of Balclutha (http://www.balclutha.org)
# 
#                All Rights Reserved
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
#
# Corporation of Balclutha DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
# SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS, IN NO EVENT SHALL Corporation of Balclutha BE LIABLE FOR
# ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE. 
#
import logging, os, sys, OFS
from App.ImageFile import ImageFile
from App.special_dtml import DTMLFile

GLOBALS = globals()
logger = logging.getLogger('lbn.zenoss')

def noop(*args, **kw): pass

#
# seems that this pesky function is removing inituser without successfully
# installing it ...
#
logger.info('monkeypatching ZenUtils.Security')
from Products.ZenUtils import Security
Security._createInitialUser = noop

#
# there is the most crapulous ipv6 support test ...
#
logger.info('turning off IPv6')
def ipv6_available():
    return False

from Products.ZenUtils import Utils
Utils.ipv6_available = ipv6_available

#
# add password type into Properties on ZMI (but since these aren't writable, it's moot)
#
from ZPublisher.Converters import type_converters, field2string
type_converters['password'] = field2string

from Products.ZenModel.ZenModelRM import ZenModelRM
ZenModelRM.manage_propertiesForm = DTMLFile('dtml/properties', GLOBALS, property_extensible_schema__=1)

logger.info('added type converters: password, keyedselection')


from Products.ZenRelations.ToManyRelationshipBase import ToManyRelationshipBase, RelationshipBase
ToManyRelationshipBase.manage_options = ToManyRelationshipBase.manage_options + OFS.SimpleItem.SimpleItem.manage_options

from Products.ZenRelations.ToManyRelationship import ToManyRelationship
_remoteRemoveOrig = ToManyRelationship._remoteRemove

def _remoteRemove(self, obj=None):
    """
    remove an object from the far side of this relationship
    if no object is passed in remove all objects
    """
    # seems the original barfs on trying to delete non-existing relations ...
    try:
        _remoteRemoveOrig(self, obj)
    except (AttributeError, ValueError):
        pass

ToManyRelationship._remoteRemove = _remoteRemove

# because this isn't within the 'Products' module namespace, we have to 
# manually manipulate misc_ - we're stuffing them into OFSP ...
from Products import OFSP
OFSP.misc_ = misc_ = {}
for icon in ('ZenossInfo_icon', 'RelationshipManager_icon', 'portletmanager'):
    misc_[icon] = ImageFile('www/%s.gif' % icon, GLOBALS)

from Products.ZenWidgets.PortletManager import PortletManager
PortletManager.icon = 'misc_/OFSP/portletmanager'

from Products.ZenModel.ZenossInfo import ZenossInfo
ZenossInfo.icon = 'misc_/OFSP/ZenossInfo_icon'

from Products.ZenRelations.RelationshipManager import RelationshipManager
RelationshipManager.icon = 'misc_/OFSP/RelationshipManager_icon'

logger.info('added ZMI icons')

# TODO - override RelationshipManager.manage_workspace to be default ...

# note that we're also strapping an implements(IItem) via zcml ...
import AccessControl
from Products.ZenRelations.ZItem import ZItem

ZItem.manage_options = AccessControl.Owned.Owned.manage_options + ( 
    {'label':'Interfaces', 'action':'manage_interfaces'}, 
    ) 


#
# the Skin registration stuff is borked for python modules, but we want to retain
# them for other zenpacks where it might still work ...
#
from Products.ZenUtils import Skins

findZenPackRootOrig = Skins.findZenPackRoot
def findZenPackRoot(base):
    # pure python module search
    if base.find('site-packages') != -1:
        dirs = base.split(os.path.sep)
        ndx = dirs.index('site-packages')
        return '.'.join(dirs[ndx + 1:-1])

    # Zenoss ZenPacks stored in Zenoss Tree
    return findZenPackRootOrig(base)

Skins.findZenPackRoot = findZenPackRoot


from Products.ZenModel.ZenPackLoader import ZPLSkins, ZPLBin, ZPLLibExec

ZPLSkinsload = ZPLSkins.load
ZPLSkinsunload = ZPLSkins.unload
ZPLBinload = ZPLBin.load
ZPLLibExecload = ZPLLibExec.load

def skinLoad(self, pack, app):
    try:
	ZPLSkinsload(self, pack, app)
    except Exception, e:
	logger.warn(str(e), exc_info=True)

def skinUnload(self, pack, app, leaveObjects=False):
    try:
	ZPLSkinsunload(self, pack, app, leaveObjects)
    except Exception, e:
	logger.warn(str(e), exc_info=True)

def binLoad(self, pack, app):
    try:
	ZPLBinload(self, pack, app)
    except Exception, e:
	logger.warn(str(e), exc_info=True)

def libexecLoad(self, pack, app):
    try:
	ZPLLibExecload(self, pack, app)
    except Exception, e:
	logger.warn(str(e), exc_info=True)

ZPLSkins.load = skinLoad
ZPLSkins.unload = skinUnload
ZPLBin.load = binLoad
ZPLLibExec.load = libexecLoad


from Products.ZenModel.ZenPack import ZenPack
ZenPack.meta_data = 'ZenPack'

def createZProperties(self, app=None, REQUEST=None):
    """
    Create zProperties in the ZenPack's self.packZProperties
    
    @param app: ZenPack
    @type app: ZenPack object
    """
    # for brand new installs, define an instance for each of the zenpacks
    # zprops on dmd.Devices
    devices = app and app.zport.dmd.Devices or self.zport.dmd.Devices
    for name, value, pType in self.packZProperties:
        if not devices.hasProperty(name):
            devices._setProperty(name, value, pType)
        if not getattr(devices, name):
            setattr(devices, name, value)
    if REQUEST:
        return self.manage_main(self, REQUEST)

ZenPack.createZProperties = createZProperties

logger.info('added ZMI-recoverable ZenPack createZProperties')


from Products.ZenUtils.CmdBase import CmdBase
getConfigFileDefaultsOrig = CmdBase.getConfigFileDefaults
def getConfigFileDefaults(self, filename):
    """
    Parse a config file 
    """
    try:
        return getConfigFileDefaultsOrig(self, filename)
    except IOError:
        pass

CmdBase.getConfigFileDefaults = getConfigFileDefaults
    
logger.info('stop zope.conf being stomped on')

pyver = sys.version[:3]
if sys <= '2.6':

    import subprocess

    def check_output(args):
        """ simplified check_output implementation for py2.6 """
        return subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]

    subprocess.check_output = check_output
    logger.info('monkeypatched subprocess.check_output')

    class NullHandler(logging.Handler):

        lock = None

        def emit(self, record):
            pass

        def handle(self, record):
            pass

        def createLock(self):
            return None

    logging.NullHandler = NullHandler
    logger.info('monkeypatched logging.NullHandler')
