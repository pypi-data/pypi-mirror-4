#
# Copyright (c) 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>
# Licenced under the GNU General Public License v3 (GPLv3)
# see file LICENSE-gpl-3.0.txt
#

__author__ = "Hartmut Goebel <h.goebel@goebel-consult.de>"
__copyright__ = "Copyright (c) 2008 by Hartmut Goebel <h.goebel@goebel-consult.de>"
__licence__ = "GPLv3 - GNU General Public License v3"

from com.sun.star.awt import XTopWindowListener, XWindowListener, \
 XFocusListener, XKeyListener, XMouseListener, XPaintListener, \
 XEventListener


class TopWindowListener(XTopWindowListener):
    #   Note that com.sun.star.lang.EventObject has the following members:
    #       Source  which is a  com.sun.star.uno.XInterface
    #           refers to the object that fired the event.

    def __init__(self, *args, **kw):
        super(self, TopWindowListener).__init__(*args, **kw)
        # Since this class implements the XTopWindowListener interface,
        #  add ourself as a listener to our own window.
        self._window.addTopWindowListener(self)
        
    def windowOpened(self, event):
        """Is invoked when a window has been opened."""
        pass

    def windowClosing(self, event):
        """Is invoked when a window is in the process of being closed.
        The close operation can be overridden at this point."""
        self._window.dispose()

    def windowClosed(self, event):
        """Is invoked when a window has been closed."""
        pass

    def windowMinimized(self, event):
        """Is invoked when a window is iconified."""
        pass

    def windowNormalized(self, event):
        """Is invoked when a window is de-iconified."""
        pass

    def windowActivated(self, event):
        """is invoked when a window is activated."""
        pass

    def windowDeactivated(self, event):
        """Is invoked when a window is de-activated."""
        pass


class WindowListener(XWindowListener):
    #   Note that com.sun.star.awt.WindowEvent has the following members:
    #       long X      long Y
    #       long Width  long Height
    #       long LeftInset    long TopInset
    #       long RightInset   long BottomInset

    def __init__(self, *args, **kw):
        super(self, WindowListener).__init__(*args, **kw)
        # Since this class implements the XWindowListener interface,
        #  add ourself as a listener to our own window.
        self._window.addWindowListener(self)

    def windowResized(self, event):
        """Is invoked when the window has been resized."""
        pass

    def windowMoved(self, event):
        """Is invoked when the window has been moved."""
        pass

    def windowShown(self, event):
        """Is invoked when the window has been shown."""
        # please note the type of parameter is described
        #  above in the comment for XTopWindowListener.
        pass

    def windowHidden(self, event):
        """Is invoked when the window has been hidden."""
        # please note the type of parameter is described
        #  above in the comment for XTopWindowListener.
        pass


class FocusListener(XFocusListener):
    #   Note that com.sun.star.awt.FocusEvent has the following members:
    #       short FocusFlags
    #       com.sun.star.uno.XInterface NextFocus
    #       boolean Temporary

    def __init__(self, *args, **kw):
        super(self, FocusListener).__init__(*args, **kw)
        # Since this class implements the XFocusListener interface,
        #  add ourself as a listener to our own window.
        self._window.addFocusListener(self)

    def focusGained(self, event):
        """Is invoked when a window gains the keyboard focus."""
        pass

    def focusLost(self, event):
        """Is invoked when a window loses the keyboard focus."""
        pass

class KeyListener(XKeyListener):
    #   Note that com.sun.star.awt.KeyEvent has the following members:
    #       short KeyCode   (constant from com.sun.star.awt.Key)
    #       char  KeyChar
    #       short KeyFunc   (constant from com.sun.star.awt.KeyFunction)

    def __init__(self, *args, **kw):
        super(self, KeyListener).__init__(*args, **kw)
        # Since this class implements the XKeyListener interface,
        #  add ourself as a listener to our own window.
        self._window.addKeyListener(self)

    def keyPressed(self, event):
        """Is invoked when a key has been pressed."""
        pass

    def keyReleased(self, event):
        """Is invoked when a key has been released."""
        pass


class MouseListener(XMouseListener):
    #   Note that com.sun.star.awt.MouseEvent has the following members:
    #       short Buttons       (constant from com.sun.star.awt.MouseButton)
    #       short X     short Y
    #       long ClickCount
    #       boolean PupupTrigger

    def __init__(self, *args, **kw):
        super(self, MouseListener).__init__(*args, **kw)
        # Since this class implements the XMouseListener interface,
        #  add ourself as a listener to our own window.
        self._window.addMouseListener(self)

    def mousePressed(self, event):
        """Is invoked when a mouse button has been pressed on a window."""
        pass

    def mouseReleased(self, event):
        """Is invoked when a mouse button has been released on a window."""
        pass

    def mouseEntered(self, event):
        """Is invoked when the mouse enters a window."""
        pass

    def mouseExited(self, event):
        """Is invoked when the mouse exits a window."""
        pass


class PaintListener(XPaintListener):
    #   Note that com.sun.star.awt.Painevent has the following members:
    #       com.sun.star.awt.Rectangle UpdateRect
    #       short Count

    def __init__(self, *args, **kw):
        super(self, PaintListener).__init__(*args, **kw)
        # Since this class implements the XPaintListener interface,
        #  add ourself as a listener to our own window.
        self._window.addPaintListener(self)

    # [oneway] void
    # windowPaint([in] Painevent event);
    def windowPaint(self, event):
        """
        Is invoked when a region of the window became invalid, e.g.
        when another window has been moved away.
        """
        pass


class EventListener(XEventListener):
    #   Note that com.sun.star.lang.EventObject has the following members:
    #       Source  which is a  com.sun.star.uno.XInterface
    #           refers to the object that fired the event.

    def __init__(self, *args, **kw):
        super(self, EventListener).__init__(*args, **kw)

    # void
    # disposing([in] com.sun.star.lang.EventObject event);
    def disposing(self, event):
        """
        Gets called when the broadcaster is about to be disposed.
        """
        pass

