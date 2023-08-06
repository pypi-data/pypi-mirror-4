#
# Copyright 2010-2012 Corporation of Balclutha (http://www.balclutha.org)
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
import logging, os, transaction, subprocess
from Acquisition import aq_base, aq_inner
from OFS.CopySupport import CopyError
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger('lbn.zenoss.zensetup')

from Products.ZenUtils.Utils import zenPath
from Products.ZenUtils.CmdBase import CmdBase
from Products.ZenModel.zenbuild import zenbuild
from Products.ZenRelations.ImportRM import ImportRM


def createZentinel(app, skipusers=True):
    """
    function to create a zport
    """
    try:
        zb = bzenbuild(app)

        #zb.options.logseverity = logging.INFO

        # hmmm - lets just accept defaults
        #zb.options.evthost,
        #zb.options.evtuser,
        #zb.options.evtpass,
        #zb.options.evtdb,
        #zb.options.evtport,
        #zb.options.smtphost,
        #zb.options.smtpport,
        #zb.options.pagecommand        

        zb.build()

        zport = app.zport

        # this is the qs-nousersetup functionality ...
        if skipusers:
            zport.dmd._rq = True

    except:
        logger.error('Create Zentinel instance failed', exc_info=True)


class bzenbuild(zenbuild):
    """
    no command-line opts zenbuild
    """
    revertables = ('index_html', 'standard_error_message')

    def __init__(self, app):
        CmdBase.__init__(self, noopts=True)
        self.app = app
        

    def build(self):
        """
        don't let zenbuild trash default Zope
        """
        transaction.begin()
        app = self.app
        for id in self.revertables:
            if app.hasObject(id):
                try:
                    app.manage_renameObject(id, '%s.save' % id)
                except CopyError:
                    # retry from earlier failure ....
                    pass

        zenbuild.build(self)

        # hmmm - wtf - reloading static data (in alphabetical order)
        loader = ImportRM()
        directory = os.path.join(os.environ['ZENHOME'], 'Products', 'ZenModel', 'data')
        for file in os.listdir(directory):
            if not file.endswith('.xml'):
                continue
            loader.loadObjectFromXML(os.path.join(directory, file))

        # move the Zenoss standard_error_message
        std_err = aq_base(app._getOb('standard_error_message', None))
        if std_err:
            app.zport._setObject('standard_error_message', std_err)

        for id in self.revertables:
            if app.hasObject(id):
                app._delObject(id)

            try:
                app.manage_renameObject('%s.save' % id, id)
            except CopyError:
                pass

        # hmmm - dunno why some of the zeninel stuff is getting zapped ..
        transaction.commit()

class ZenSetup(BrowserView):
    """
    Creates a Zenoss installation
    """

    def debug(self):
	"""
	ensure product installed, placeholder to present installation info
	"""
	return 'lbn.zenoss browser views are registered'

    def createZentinel(self, skipusers=True):
        """
        creates zport, DMD in install root
        """
        context = aq_inner(self.context)

        createZentinel(context,skipusers)

        self.request.set('manage_tabs_message', 'created zenoss dmd')
        self.request.RESPONSE.redirect('zport/dmd')


    def createMySql(self):
        """
        setup (local) MySQL for Events processing
        """
        MYSQL = 'mysql --user=root'

        # TODO - put stdin redirects into pipe!!!
        for cmd in ('%s create database events' % MYSQL,
                    '% events < %s/Products/ZenEvents/db/zenevents.sql' % (MYSQL, os.environ['ZENHOME']),
                    '% events < %s/Products/ZenEvents/db/zenprocs.sql' % (MYSQL, os.environ['ZENHOME'])):
            try:
                pipe = subprocess.Popen(cmd.split(' '), 
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE)
            except OSError, e:
                raise OSError, '%s: %s' % (cmd, str(e))        

        self.request.set('manage_tabs_message', 'created MySQL')
        self.request.redirect('manage_main')
