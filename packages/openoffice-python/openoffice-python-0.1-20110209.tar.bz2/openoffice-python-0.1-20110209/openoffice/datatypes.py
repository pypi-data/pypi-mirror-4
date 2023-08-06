#
# Copyright (c) 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>
# Licenced under the GNU General Public License v3 (GPLv3)
# see file LICENSE-gpl-3.0.txt
#

__author__ = "Hartmut Goebel <h.goebel@goebel-consult.de>"
__copyright__ = "Copyright (c) 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>"
__licence__ = "GPLv3 - GNU General Public License v3"


def Array(*args):
    """
    This is just sugar coating so that code from OOoBasic which
    contains the Array() function can work perfectly in PYTHON.
    """
    return tuple(args)
