# -*- mode: python ; coding: utf-8 -*-
#
# Copyright (c) 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>
# Licenced under the GNU General Public License v3 (GPLv3)
# see file LICENSE-gpl-3.0.txt
#

__author__ = "Hartmut Goebel <h.goebel@goebel-consult.de>"
__copyright__ = "Copyright (c) 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>"
__licence__ = "GPLv3 - GNU General Public License v3"

import uno
from com.sun.star.beans import PropertyValue

def iter(elems, prefix=''):
    # todo: getByIndex verwenden??
    if hasattr(elems, 'createEnumeration'):
        enumerator = elems.createEnumeration()
        while enumerator.hasMoreElements():
            yield enumerator.nextElement()
    else:
        for name in elems.ElementNames:
            if name.startswith(prefix):
                yield elems.getByName(name)

def Properties(**kw):
    return  tuple([PropertyValue(k, 0, v,0)
                   for k,v in kw.iteritems()])
