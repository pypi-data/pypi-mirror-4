#**********************************************************************
#
#   Danny.OOo.ConfigLib.py
#
#   A module to easily work with OpenOffice.org.
#
#**********************************************************************
#   Copyright (c) 2003-2004 Danny Brewer
#   d29583@groovegarden.com
#
#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Lesser General Public
#   License as published by the Free Software Foundation; either
#   version 2.1 of the License, or (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Lesser General Public License for more details.
#
#   You should have received a copy of the GNU Lesser General Public
#   License along with this library; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#   See:  http://www.gnu.org/licenses/lgpl.html
#
#**********************************************************************
#   If you make changes, please append to the change log below.
#
#   Change Log
#   Danny Brewer         Revised 2004-06-20-01
#
#**********************************************************************


# OOo's libraries
import uno

#from com.sun.star.beans import PropertyValue

import openoffice
from openoffice import Properties


def getConfigAccess(nodePath, writeAccess=False, enableSync=True,
                    lazyWrite=False):
    """An easy way to obtain a configuration node from the configuration manager."""
    localContext = uno.getComponentContext()
    configProvider = localContext.ServiceManager.createInstanceWithArguments(
        "com.sun.star.configuration.ConfigurationProvider",
        Properties(enablesync=enableSync))
   
    if writeAccess:
        serviceName = "com.sun.star.configuration.ConfigurationUpdateAccess"
    else:
        serviceName = "com.sun.star.configuration.ConfigurationAccess"

    configAccess = configProvider.createInstanceWithArguments(serviceName,
        Properties(nodepath=nodePath, lazywrite=lazyWrite))

    return configAccess


if __name__ == '__main__':
    print '-- AddonUI --'
    cfg = getConfigAccess("/org.openoffice.Office.Addons/AddonUI")
    for name in cfg.ElementNames:
        print name #, cfg.getByName(name)
        #print
    elem = cfg.getByName("AddonMenu")
    #import pyXray
    #import openoffice.interact
    #ctx = openoffice.interact.Context()
    #pyXray.XrayBox(ctx.context, elem)
    #for name in elem.ElementNames:
    #    print name, cfg.getByName(name)
    #    print
    #for name in openoffice.iter(elem):
    #    print dir(name) #.value
        
    #for name in elem.getElementNames():

    print '-- Some user data --'
    cfg = getConfigAccess("/org.openoffice.UserProfile/Data")
    print 'Organisation', cfg.o
    print 'Firstname', cfg.givenname
    print 'Lastname', cfg.sn
    print 'Initials', cfg.initials
    print 'Title', cfg.title
    print 'Position', cfg.position
    print 'Email', cfg.mail
