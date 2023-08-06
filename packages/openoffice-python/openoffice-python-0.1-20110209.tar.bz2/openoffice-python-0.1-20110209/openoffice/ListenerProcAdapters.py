#**********************************************************************
#
#   Danny.OOo.Listeners.ListenerProcAdapters.py
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
#   Danny Brewer         Revised 2004-06-05-01
#
#**********************************************************************


# OOo's libraries
import uno
import unohelper
from com.sun.star.awt import XActionListener, XItemListener, XTextListener

__all__ = ['ActionListenerAdapter', 'ItemListenerAdapter',
           'TextListenerAdapter']

class __ProcAdapter_MixIn:
    """An ActionListener adapter.

    When actionPerformed is called, this will call an arbitrary python
    procedure, with this signature:

         procToCall(actionEvent, *args)

    1. the oActionEvent
    2. any other parameters you specified to this object's constructor
       (as a tuple).
    """
    def __init__(self, procToCall, args=()):
        self.procToCall = procToCall
        self.args = args # additional arguments to be passed to procToCall
        super(__ProcAdapter_MixIn, self).__init__()



class ActionListenerAdapter(__ProcAdapter_MixIn, unohelper.Base, XActionListener):
    """This class implements com.sun.star.awt.XActionListener."""
    def actionPerformed(self, event):
        # event is a com.sun.star.awt.ActionEvent struct.
        return self.procToCall(event, *self.args)
    
class ItemListenerAdapter(__ProcAdapter_MixIn, unohelper.Base, XItemListener):
    # This object implements com.sun.star.awt.XItemListener.

    def itemStateChanged(self, event):
        # event is a com.sun.star.awt.ItemEvent struct.
        return self.procToCall(event, *self.args)

class TextListenerAdapter(__ProcAdapter_MixIn, unohelper.Base, XTextListener):
    # This object implements com.sun.star.awt.XTextistener.

    def textChanged( self, event):
        # event is a com.sun.star.awt.TextEvent struct.
        return self.procToCall(event, *self.args)
