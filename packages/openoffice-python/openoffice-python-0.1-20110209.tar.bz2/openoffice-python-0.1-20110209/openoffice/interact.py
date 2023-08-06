#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>
# Licenced under the GNU General Public License v3 (GPLv3)
# see file LICENSE-gpl-3.0.txt
#

__author__ = "Hartmut Goebel <h.goebel@goebel-consult.de>"
__copyright__ = "Copyright (c) 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>"
__licence__ = "GPLv3 - GNU General Public License v3"

import unohelper
import openoffice.officehelper as officehelper
from com.sun.star.beans import PropertyValue

import openoffice.streams

import os

class Context:
    # Todo:
    # - Make desktop, unoService and coreRelefection into slots (or such)
    # - find out which objects are singletons anyway
    def __init__(self, pipename=None, host=None, port=None):
        """Start OOo and connect to it"""
        self.context = officehelper.bootstrap(pipename=pipename,
                                              host=host, port=port)
        self._desktop = None

    def desktop(self):
        if self._desktop is None:
            self._desktop = Desktop(self)
        return self._desktop

    def unoService(self, className):
        return self.context.ServiceManager.createInstanceWithContext(className,
                                                                     self.context)

    def coreReflection(self):
        return self.createUnoService("com.sun.star.reflection.CoreReflection")

    def ceateUnoStruct(self, typeName):
        """
        Create a UNO struct.
        Similar to the function of the same name in OOo Basic.
        """
        # Get the IDL class for the type name
        idlClass = self.coreReflection().forName(typeName)
        rv, struct = idlClass.createObject(None)
        return struct
    
    #----  API helpers ---------------

    def hasUnoInterfaces(self, obj, *interfaceNames):
        """
        Similar to Basic's HasUnoInterfaces() function.
        """
        wantedInterfaces = set(interfaceNames)
        # Get the Introspection service and the object info
        introspect = self.createUnoService("com.sun.star.beans.Introspection")
        objInfo = introspect.inspect( oObject )
   
        # Get List of all methods of the object.
        methods = objInfo.getMethods(uno.getConstantByName("com.sun.star.beans.MethodConcept.ALL"))
        # Get the classes (=interfaces) these methods are defined by
        supportedInterfaces = set([method.getDeclaringClass().getName()
                                   for method in methods])
        return wantedInterfaces <= supportedInterfaces


class Desktop:
    def __init__(self, ctx=None, pipename=None, host=None, port=None):
        if ctx is None:
            ctx = Context(pipename=pipename, host=host, port=port)
        self._ctx = ctx
        # Verbindung zur Oberflaeche
        self._desktop = ctx.context.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", ctx.context)
        self._ctx._desktop = self._desktop


    def newDoc(self, doctype, **kw):
        """
        Create a new document.

        ''doctype'' may be one of swriter, scalc, simpress, sdraw,
        smath or sbase.
        """
        return self.openURL("private:factory/" + doctype, **kw)


    def openURL(self, url, target='_default', hidden=False,
                readonly=False, preview=False, stream=None):
        """
        Open a document from it's URL.

        This argumens will be passed to loadComponentFromURL() as
        Properties:

        - hidden: do not open windows for this document, hide it
        - readonly: open in read-only mode
        - preview: open in preview mode
        - stream: use this stream as "InputStream" (only usefull with
                  url='private:stream'. You should use openStream() instead.
        
        Allowed values for 'target' are:

        :_self: Returns the frame itself. The same as with an empty
               target frame name. This means to search for a frame you
               already have, but it is legal.
        :_top: Returns the top frame of the called frame. The first
               frame where isTop() returns true when traveling up the
               hierarchy. If the starting frame does not have a parent
               frame, the call is treated as a search for "_self".
               This behavior is compatible to the frame targeting in a
               web browser.
        :_parent: Returns the next frame above in the frame hierarchy.
               If the starting frame does not have a parent frame, the
               call is treated as a search for "_self". This behavior
               is compatible to the frame targeting in a web browser.
        :_blank: Creates a new top-level frame as a child frame of the
               desktop. If the called frame is not part of the desktop
               hierarchy, this call fails. Using the "_blank" target
               loads open documents again that result in a read-only
               document, depending on the UCB content provider for the
               component. If loading is done as a result of a user
               action, this becomes confusing to theusers, therefore
               the "_default" target is recommended in calls from a
               user interface, instead of "_blank". Refer to the next
               section for a discussion about the _default target..
        :_default: Similar to "_blank", but the implementation defines
               further behavior that has to be documented by the
               implementer. The com.sun.star.frame.XComponentLoader
               implemented at the desktop object shows the following
               default behavior.
        """
        properties = (
            PropertyValue("Hidden",   0, bool(hidden), 0),
            PropertyValue("ReadOnly", 0, bool(readonly), 0),
            PropertyValue("Preview",  0, bool(preview), 0),
            PropertyValue("InputStream", 0, stream, 0),
            )
        return self._desktop.loadComponentFromURL(url, target, 0, properties)

    def openFile(self, filename, **kw):
        filename = os.path.expanduser(filename)
        filename = os.path.abspath(filename)
        url = unohelper.systemPathToFileUrl(filename)
        return self.openURL(url, **kw)

    def openStream(self, filehandle, **kw):
        if not isinstance(filehandle, openoffice.streams.InputStream):
            filehandle = openoffice.streams.InputStream(filehandle)
        return self.openURL("private:stream", stream=filehandle, **kw)

        
if __name__ == '___main__':
    desktop = Desktop()
    doc = desktop.newDoc("swriter")
