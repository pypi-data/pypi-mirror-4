#----------------------------------------------------------------------
# Nive cms
# Copyright (C) 2012  Arndt Droullier, DV Electric, info@dvelectric.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#----------------------------------------------------------------------

import string
from types import StringType, UnicodeType, IntType, LongType
from nive.utils.utils import ConvertListToStr, ConvertToNumberList

from nive.definitions import StagPage, StagPageElement
from nive.i18n import _


class ObjCopy:
    """
    Cut, copy and paste functionality for objects 
    """
    
    def CanCopy(self):
        """
        """
        return not hasattr(self, "disableCopy") or not self.disableCopy


    def CanPaste(self):
        """
        """
        return False



class ContainerCopy:
    """
    Cut, copy and paste functionality for object container
    """
    
    def CanCopy(self):
        """
        """
        return not hasattr(self, "disableCopy") or not self.disableCopy


    def CanPaste(self):
        """
        """
        return not hasattr(self, "disablePaste") or not self.disablePaste


    def Paste(self, ids, user):
        """
        Paste the copied object with id to this object
        """
        root = self.GetRoot()
        new = []
        msgs = []
        result = True
        for id in ids:
            id = int(id)
            if self.GetID() == id:
                continue
            obj = root.LookupObj(id, preload="skip")
            if not obj:
                msgs.append(_(u"Object not found"))
                result = False
                continue
            newobj = self.Duplicate(obj, user) 
            if not newobj:
                raise TypeError, "Duplicate failed"
            new.append(new)
        if not self.app.configuration.autocommit:
            for o in new:
                o.Commit(user)
        return result, msgs
    

    def Move(self, ids, user):
        """
        Move the object with id to this object
        
        Events
        
        - beforeCreate(data=obj.meta, type=type)
        - afterDelete(id=obj.id)
        - moved()
        """
        root = self.root()
        oldParent=None

        moved = []
        msgs = []
        result = True
        for id in ids:
            id = int(id)
            if self.GetID() == id:
                continue
            obj = root.LookupObj(id, preload="skip")
            if not obj:
                msgs.append(_(u"Object not found"))
                result = False
                continue

            type=obj.GetTypeID()
            # allow subobject
            if not self.IsTypeAllowed(type, user):
                raise TypeError, "Object cannot be added here"

            self.Signal("beforeCreate", data=obj.meta, type=type)
            if not oldParent or oldParent.id != obj.GetParent().id:
                oldParent = obj.GetParent()
            obj.__parent__ = self
            obj.meta["pool_unitref"] = self.GetID()
            oldParent.Signal("afterDelete", id=obj.id)
            obj.Signal("moved")
            #obj.Close()
            moved.append(obj)

        for o in moved:
            o.Commit(user)
        return result, msgs
    


class CopyView:
    """
    View functions for cut, copy and paste
    """
    CopyInfoKey = "CCP__"

    def cut(self):
        """
        """
        ids = self.GetFormValue(u"ids")
        if not ids:
            ids = [self.context.id]
        cp = self.SetCopyInfo(u"cut", ids, self.context)
        url = self.GetFormValue(u"url")
        if not url:
            url = self.PageUrl(self.context)
        msgs = _(u"OK")
        ok = True
        return self.Redirect(url, [ok, msgs])


    def copy(self):
        """
        """
        ids = self.GetFormValue(u"ids")
        if not ids:
            ids = [self.context.id]
        cp = self.SetCopyInfo(u"copy", ids, self.context)
        url = self.GetFormValue(u"url")
        if not url:
            url = self.PageUrl(self.context)
        msgs = _(u"OK")
        ok = True
        return self.Redirect(url, [ok, msgs])


    def paste(self):
        """
        """
        deleteClipboard=1
        url = self.GetFormValue(u"url")
        if not url:
            url = self.PageUrl(self.context)
        action, ids = self.GetCopyInfo()
        if not action or not ids:
            msgs = []
            return self.Redirect(url, msgs)

        pepos = self.GetFormValue(u"pepos")
        result = False
        msgs = _(u"Method unknown")
        if action == u"cut":
            result, msgs = self.context.Move(ids, self.User())
            if result and deleteClipboard:
                cp = self.DeleteCopyInfo()
        elif action == u"copy":
            result, msgs = self.context.Paste(ids, user=self.User())

        return self.Redirect(url, [result, msgs])
    
    
    def SetCopyInfo(self, action, ids, context):
        """
        store in session or cookie
        """
        if not ids:
            return u""
        if type(ids) in (StringType,UnicodeType):
            ids=ConvertToNumberList(ids)
        cp = ConvertListToStr([action]+ids).replace(u" ",u"")
        self.request.session[self.CopyInfoKey] = cp
        return cp


    def GetCopyInfo(self):
        """
        get from session or cookie
        """
        cp = self.request.session.get(self.CopyInfoKey,u"")
        if type(cp) in (StringType,UnicodeType):
            cp = cp.split(u",")
        if not cp or len(cp)<2:
            return u"", []
        return cp[0], cp[1:]

    
    def ClipboardEmpty(self):
        """
        check if clipboard is empty
        """
        cp = self.request.session.get(self.CopyInfoKey,u"")
        return cp==u""
    

    def DeleteCopyInfo(self):    
        """
        reset copy info
        """
        self.request.session[self.CopyInfoKey] = u""


    # widgets ------------------------------------------------------
    
    def shortcut_cut(self):
        if not self.context.CanCopy():
            return u""
        static = self.StaticUrl(StaticMod)
        param = self.FmtURLParam(ids=self.context.GetID())
        l = u"""<a href="cut?%(param)s"><img src="%(static)simages/cut.png" title="%(title)s" align="top" /> </a>
        """ % {u"param": p, u"static": static, u"title": _(u"Cut and copy to clipboard")}
        html = u"""<div class="unit_options_block">%s</div>""" % (l)
        return html

    def shortcut_copy(self):
        if not self.context.CanCopy():
            return u""
        static = self.StaticUrl(StaticMod)
        param = self.FmtURLParam(ids=self.context.GetID())
        l = u"""<a href="copy?%(param)s"><img src="%(static)simages/copy.png" title="%(title)s" align="top" /> </a>
        """ % {u"param": p, u"static": static, u"title": _(u"Copy to clipboard")}
        html = u"""<div class="unit_options_block">%s</div>""" % (l)
        return html

    def shortcut_paste(self):
        if not self.context.CanPaste():
            return u""
        static = self.StaticUrl(StaticMod)
        l = u"""<a href="paste"><img src="%(static)simages/paste.png" title="%(title)s" align="top" /> </a>
        """ % {u"param": p, u"static": static, u"title": _(u"Paste clipboard")}
        html = u"""<div class="unit_options_block">%s</div>""" % (l)
        return html

    
    
    
    