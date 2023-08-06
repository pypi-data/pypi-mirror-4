# -*- mode: python ; coding: utf-8 -*-
#
# Copyright (c) 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>
# Licenced under the GNU General Public License v3 (GPLv3)
# see file LICENSE-gpl-3.0.txt
#
# Originally based on officehelper.py 1.2 comming with OOo
#

__author__ = "Hartmut Goebel <h.goebel@goebel-consult.de>"
__copyright__ = "Copyright (c) 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>"
__licence__ = "GPLv3 - GNU General Public License v3"

import os
import random
import sys
from time import sleep

import uno
from com.sun.star.connection import NoConnectException

class BootstrapException(Exception): pass

__soffice_executable = None
    
def _build_connect_string(pipename=None, host=None, port=None):
    """
    Returns a connection description string to be used to connect to
    this process via UnoUrlResolver().resolve().

    Pass either a pipename for a named pipe or host and port for a
    socket connection.

    Note: You should use the naemd pipe whenever possible, since
    socket are unsecure: Everybody can connect to a socket and access
    your documents without any access control.
    """
    if pipename:
        connectString = "pipe,name=%s" % pipename
    else:
        connectString = 'socket'
        if host: connectString += ',host='+str(host)
        if port: connectString += ',port='+str(port)
    return connectString


def _build_cmd_args(connectString, unaccept=False):
    """
    Returns command arguments (including executable and options)
    suitable for staring an background OOo instance listening on named
    pipe or socket descripted in parameter 'connectString'.

    If unaccept is true, the parmeter '-accept=...' will become
    '-unaccept=...' for making the instance unlisten.
    """

    def find_executable():
        """
        Find 'soffice' executable.

        Normaly soffice should be in the same directory as uno.py, but eg.
        Debian does not obaj to this convention. Thus we need to search
        the executable.
        """
        global __soffice_executable
        if __soffice_executable:
            return __soffice_executable
        for p in [os.path.dirname(uno.__file__),
                  '/opt/libreoffice/program',
                  '/usr/lib/libreoffice/program',
                  '/usr/lib/openoffice/program',
                  '/usr/lib/ooo/program',
                  '/usr/bin',
                  '/usr/local/bin',
                  ]:
            office = os.path.join(p, "soffice")
            if os.path.exists(office):
                break
        else:
            import glob
            pathes = glob.glob('/usr/lib/ooo-[234].*/program/soffice')
            if not pathes:
                raise BootstrapExceptions('soffice executable not found')
            pathes.sort(reverse=True)
            office = pathes[0]
        __soffice_executable = office
        return office

    # soffice script used on *ix, Mac; soffice.exe used on Windoof
    office = find_executable()
    if sys.platform.startswith("win"):
        office += ".exe"

    # -headless includes -invisible (which includes -nologo -nodefault)
    accept = unaccept and '-unaccept' or '-accept'
    cmdArray = (office,
                "-headless", "-norestore", "%s=%s;urp;" %
                (accept, connectString))
    return cmdArray


def _start_OOo(connectString):
    """Start an OOo process listening on named pipe or socket
    descripted in parameter 'connectString'.
    """
    cmdArray = _build_cmd_args(connectString)
    # Start the office proces, don't check for exit status since
    # an exception is caught anyway if the office terminates
    # unexpectedly.
    return os.spawnv(os.P_NOWAIT, cmdArray[0], cmdArray)


def connect(connectString):
    """
    Connect to an OOo instance listening on named pipe or socket
    descripted in parameter 'connectString'.
    """
    localContext = uno.getComponentContext()
    resolver = localContext.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", localContext)
    connect = "uno:" + connectString + ";urp;StarOffice.ComponentContext"

    # Wait until an office is started, but loop only 20 times (10 seconds)
    for i in range(20):
        try:
            context = resolver.resolve(connect)
            break
        except NoConnectException:
            sleep(0.5)  # Sleep 1/2 second.
    else:
        # for-loop completed without 'break' (this is: no connection found)
        raise BootstrapException("Cannot connect to soffice server.")

    return context


def bootstrap(pipename=None, host=None, port=None):
    """Bootstrap OOo and PyUNO Runtime.

    If either pipename, host or port are given, connect to the OOo
    instance listening on this pipe or hosst/port. (This is mainly for
    convenience, so programms do not need to distinguish these cases.)

    If non of these parameters are give, the soffice process is
    started opening a named pipe of random name, then the local
    context is used to access the pipe.

    This function directly returns the remote component context, from
    whereon you can get the ServiceManager by calling
    getServiceManager() on the returned object.
    """
    if pipename or host or port:
        connectString = _build_connect_string(pipename=pipename,
                                              host=host, port=port)
    else:
        # Generate a random pipe name.
        pipename = "uno" + str(random.random())[2:]
        connectString = _build_connect_string(pipename=pipename)
        # start OOo listening on this named pipe
        _start_OOo(connectString)
    # get component context and return it
    context = connect(connectString)
    return context
