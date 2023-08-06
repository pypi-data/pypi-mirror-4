#!/usr/bin/env python
# -*- coding: utf-8 -*-
#**********************************************************************
#
#  PrintToWriter.py - sample script for openoffice-python
#
# This implements a simple class which makes it easy and convenient
# to print a bunch of text into a Writer document.
#
#  http://openoffice-python.origo.ethz.ch/
#
#**********************************************************************
#
# Copyright (c) 2003-2004 Danny Brewer <d29583@groovegarden.com>
# Copyright (c) 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of the
# License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#
# See:  http://www.gnu.org/licenses/lgpl.html
#
#**********************************************************************
#
# If you make changes, please append to the change log below.
#
# Change Log
# Danny Brewer     2004-06-05 Revised 
# Hartmut Goebel   2008-03-09 Major changes, adopted for
#                             openoffice-python
#
#**********************************************************************

import uno
import openoffice.interact

_ControlCharacter = "com.sun.star.text.ControlCharacter"

PARAGRAPH_BREAK  = uno.getConstantByName(_ControlCharacter+ ".PARAGRAPH_BREAK")
LINE_BREAK       = uno.getConstantByName(_ControlCharacter+ ".LINE_BREAK")
HARD_HYPHEN      = uno.getConstantByName(_ControlCharacter+ ".HARD_HYPHEN")
SOFT_HYPHEN      = uno.getConstantByName(_ControlCharacter+ ".SOFT_HYPHEN")
HARD_SPACE       = uno.getConstantByName(_ControlCharacter+ ".HARD_SPACE")
APPEND_PARAGRAPH = uno.getConstantByName(_ControlCharacter+ ".APPEND_PARAGRAPH")

class PrintToWriter:
    """
    A class which allows conveniently printing stuff into a Writer
    document.
    
    Very useful for debugging, general output purposes, or even for
    creating reports.
    """
    
    def __init__(self, desktop=None):
        if not desktop:
            desktop = openoffice.interact.Desktop() # todo: defaultDesktop?
        self._doc = desktop.newDoc('swriter', )#target='_blank', hidden=1)
        self._text = self._doc.getText()
        self._cursor = self._text.createTextCursor()

    def writeControlCharacter(self, char, absorb=False):
        # todo: what does 'absort' mean?
        self._text.insertControlCharacter(self._cursor, char, absorb)

    def write(self, string, absorb=False):
        self._text.insertString(self._cursor, str(string), absorb)

    def writelines(self, lines, absorb=False):
        for line in lines:
            self._text.insertString(self._cursor, line, absorb)

    def writeTab(self, absorb=False):
        self.write("\t", absorb)

    def paragraphBreak(self, absorb=False):
        self.writeControlCharacter(PARAGRAPH_BREAK, absorb)

    def writeLn(self, *args):
        self.writelines(args)
        self.paragraphBreak()

    def writeTabSeparated(self, *args):
        if not args:
            return
        arg = args[0]
        self.write(arg)
        for arg in args[1:]:
            self.writeTab()
            self.write(arg)


if __name__ == '__main__':
    """
    An example of how to use the PrintToWriter class to trivially
    create a new Writer document, and write out text into it.
    """
    doc = PrintToWriter()
    doc.writeLn("Hello World")
    doc.writeTabSeparated("String", 123, 456.23, True)
    doc.writeLn()
    doc.writeLn()

    doc.writeLn("Tab delimited values ...")
   
    doc.writeTabSeparated(123, 456, 789); doc.writeLn()
    doc.writeTabSeparated(465, 522, 835); doc.writeLn()
    doc.writeTabSeparated(886, 164, 741); doc.writeLn() 
