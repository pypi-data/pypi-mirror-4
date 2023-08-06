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

import openoffice.interact

def loadAsStream(odf_filename, opts=None):
    desktop = openoffice.interact.Desktop(host=opts.host, port=opts.port)

    stream = open(odf_filename)
    if 0:
        # using a file-like object works, too
        import StringIO
        stream = StringIO.StringIO(stream.read())

    doc = desktop.openStream(stream, hidden=True)
    doc.dispose()


if __name__ == '__main__':
    import optparse
    parser = optparse.OptionParser('%prog [options] ODF-Filename')
    group = parser.add_option_group('To connect to already running server use:')
    group.add_option('--host',  #default='localhost',
                     help="hostname/ip of server (default: %default)")
    group.add_option('--port',  default=2002, type=int,
                     help="port the server is listening on (default: %default)")

    opts, args = parser.parse_args()
    if len(args) != 1:
        parser.error('expects exactly one argument')
    if not opts.host:
        opts.port = None
    loadAsStream(*args, **{'opts': opts})
