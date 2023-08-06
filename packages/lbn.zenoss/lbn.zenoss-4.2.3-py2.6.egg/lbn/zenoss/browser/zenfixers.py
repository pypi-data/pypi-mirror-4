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
from Acquisition import aq_base, aq_inner
from Products.Five.browser import BrowserView


def delObject(context, id, tp=1, suppress_events=False):
    """
    strong medicine to overcome all these f**ked relation objects
    """
    ob = context._getOb(id)
    if getattr(aq_base(ob), '_objects', None):
        ob._objects = ()
        try:
            ob._v__object_deleted__ = 1
        except:
            pass
    context._objects = tuple([i for i in context._objects
                              if i['id'] != id])
    context._delOb(id)


class FixerMethods(BrowserView):

    def fixZenPackManager(self):
        """
        packs with missing/broken objects get left in the packs Relation
        """
        context = aq_inner(self.context)

        packs = context.zport.dmd.packs
        
        for id in packs.objectIds():
            pack = packs._getOb(id)
            if pack.getId() != id:
                delObject(packs, id)

        self.request.RESPONSE.redirect('manage_main')

    def deletePacks(self):
        """
        packs has actually been moved to ZenPackManger
        """
        context = aq_inner(self.context)

        dmd = context.zport.dmd
        if getattr(aq_base(dmd), 'packs', None):
            delObject(dmd, 'packs')
        
        self.request.RESPONSE.redirect('manage_main')
