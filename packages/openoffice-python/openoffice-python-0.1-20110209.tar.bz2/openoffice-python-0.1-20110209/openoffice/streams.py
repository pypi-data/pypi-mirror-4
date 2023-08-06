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

import uno
import unohelper
from com.sun.star.io import XInputStream, XOutputStream, XSeekable

class InputStream(unohelper.Base, XInputStream, XSeekable):
    def __init__(self, stream):
        self.f = stream

    def skipBytes(self, count):
        self.f.read(count)

    def readBytes(self, retSeq, count):
        s = self.f.read(count)
        return len(s), uno.ByteSequence(s)

    def readSomeBytes(self, retSeq , count):
        return self.readBytes(retSeq, count)

    def available(self):
        return 0

    def closeInput(self):
        self.f.close()

    def seek(self, pos):
        self.f.seek(pos)

    def getPosition(self):
        return self.f.tell()
    
    def getLength(self):
        f = self.f # shortcut
        pos = f.tell()
        f.seek(0, 2)
        len = f.tell()
        f.seek(pos)
        return len
    

class OutputStream(unohelper.Base, XOutputStream):
    def __init__(self, stream):
        self.f = stream

    def writeBytes(self, seq):
        self.f.write(seq.value)

    def closeOutput(self):
        self.f.flush()

    def flush(self):
        self.f.flush()
