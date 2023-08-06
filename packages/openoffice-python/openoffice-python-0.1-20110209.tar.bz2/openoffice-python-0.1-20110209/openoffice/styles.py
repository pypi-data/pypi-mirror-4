#
# Copyright (c) 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>
# Licenced under the GNU General Public License v3 (GPLv3)
# see file LICENSE-gpl-3.0.txt
#

__author__ = "Hartmut Goebel <h.goebel@goebel-consult.de>"
__copyright__ = "Copyright (c) 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>"
__licence__ = "GPLv3 - GNU General Public License v3"

class NoSuchStyleFamily(Exception): pass

def getStyle(doc, family, name):
    """
    Lookup a style from the document.
    """
    styleFamily = doc.getStyleFamilies().getByName(family)
    if not styleFamily:
        raise NoSuchStyleFamily(family)
    style = None
    if styleFamily.hasByName(name):
        style = styleFamily.getByName(name)
    return style


def defineStyle( doc, family, name, parent=None):
    """
    Add a new style to the style catalog if it is not already present.
    This returns the style object so that you can alter its properties.
    """
    styleFamily = doc.getStyleFamilies().getByName(family)
    if not styleFamily:
        raise NoSuchStyleFamily(family)

    style = None
    if styleFamily.hasByName(name):
        style = styleFamily.getByName(name)
    if not style:
        # Create new style object
        style = doc.createInstance("com.sun.star.style.Style")
        # Set its parent style
        if parent is not None:
            parentName = parent.Name # todo: is this correct?
            style.setParentStyle(parentName)
        # Add the new style to the style family
        styleFamily.insertByName(name, style)
    return style

