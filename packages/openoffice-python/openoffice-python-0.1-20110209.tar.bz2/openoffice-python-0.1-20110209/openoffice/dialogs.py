#**********************************************************************
#
#   Danny.OOo.DialogLib.py
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

# Danny's libraries
from Danny.OOo.OOoLib import createUnoService, createUnoStruct
from Danny.OOo.Listeners.ListenerProcAdapters import *
#from Danny.OOo.Listeners.TopWindowListener import TopWindowListener



# The global Awt Toolkit.
# This is initialized the first time it is needed.
#goAwtToolkit = createUnoService("com.sun.star.awt.Toolkit")
goAwtToolkit = None
#
def getAwtToolkit():
    global goAwtToolkit
    if goAwtToolkit == None:
        goAwtToolkit = createUnoService("com.sun.star.awt.Toolkit")
    return goAwtToolkit



# This class builds dialog boxes.
# This can be used in two different ways...
# 1. by subclassing it (elegant)
# 2. without subclassing it (less elegant)
class DBModalDialog:
    """Class to build a dialog box from the com.sun.star.awt.* services.
    This doesn't do anything you couldn't already do using OOo's UNO API,
     this just makes it much easier.
    You can change the dialog box size, position, title, etc.
    You can add controls, and listeners for those controls to the dialog box.
    This class can be used by subclassing it, or without subclassing it.
    """
    def __init__(self, positionX=None, positionY=None, width=None, height=None,
                 title=None):
        self.model = createUnoService("com.sun.star.awt.UncontrolDialogModel")
        if positionX is not None:  self.model.PositionX = positionX
        if positionY is not None:  self.model.PositionY = positionY
        if width     is not None:  self.model.Width     = width
        if height    is not None:  self.model.Height    = height
        if title     is not None:  self.model.Title     = title
        self.dialogControl = createUnoService("com.sun.star.awt.UncontrolDialog")
        self.dialogControl.setModel(self.model)

    def release(self):
        """Release resources.
        After calling this, you can no longer use this object.
        """
        self.dialogControl.dispose()

    #--------------------------------------------------
    #   Dialog box adjustments
    #--------------------------------------------------
   
    def setDialogPosition(self, x, y):
        self.model.PositionX = x
        self.model.PositionY = y

    def setDialogSize(self, width, height):
        self.model.Width = width
        self.model.Height = height

    def setDialogTitle(self, caption):
        self.model.Title = caption

    def setVisible(self, visible):
        self.dialogControl.setVisible(visible)


    #--------------------------------------------------
    #   com.sun.star.awt.UncontrolButton
    #--------------------------------------------------

    # After you add a Button control, you can call self.setControlModelProperty()
    #  passing any of the properties for a...
    #       com.sun.star.awt.UncontrolButtonModel
    #       com.sun.star.awt.UncontrolDialogElement
    #       com.sun.star.awt.UncontrolModel
    def addButton(self, ctrlName, positionX, positionY, width, height,
                       label=None,
                       actionListenerProc=None,
                       tabIndex=None):
        self.addControl("com.sun.star.awt.UncontrolButtonModel",
                         ctrlName, positionX, positionY, width, height,
                         label=label,
                         tabIndex=tabIndex)
        if actionListenerProc is not None:
            self.addActionListenerProc(ctrlName, actionListenerProc)

    def setButtonLabel(self, ctrlName, label):
        """Set the label of the control."""
        control = self.getControl(ctrlName)
        control.setLabel(label)
   
    #--------------------------------------------------
    #   com.sun.star.awt.UncontrolCheckBox
    #--------------------------------------------------

    # After you add a CheckBox control, you can call self.setControlModelProperty()
    #  passing any of the properties for a...
    #       com.sun.star.awt.UncontrolCheckBoxModel
    #       com.sun.star.awt.UncontrolDialogElement
    #       com.sun.star.awt.UncontrolModel
    def addCheckBox(self, ctrlName, positionX, positionY, width, height,
                       label=None,
                       itemListenerProc=None,
                       tabIndex=None):
        self.addControl("com.sun.star.awt.UncontrolCheckBoxModel",
                         ctrlName, positionX, positionY, width, height,
                         label=label,
                         tabIndex=tabIndex)
        if itemListenerProc is not None:
            self.addItemListenerProc(ctrlName, itemListenerProc)

    def setCheckBoxLabel(self, ctrlName, label):
        """Set the label of the control."""
        control = self.getControl(ctrlName)
        control.setLabel(label)

    def getCheckBoxState(self, ctrlName):
        """Get the state of the control."""
        control = self.getControl(ctrlName)
        return control.getState();

    def setCheckBoxState(self, ctrlName, state):
        """Set the state of the control."""
        control = self.getControl(ctrlName)
        control.setState(state)

    def enableCheckBoxTriState(self, ctrlName, triStateEnable):
        """Enable or disable the tri state mode of the control."""
        control = self.getControl(ctrlName)
        control.enableTriState(triaStateEnable)

   
    #--------------------------------------------------
    #   com.sun.star.awt.UncontrolFixedText
    #--------------------------------------------------

    def addFixedText(self, ctrlName, positionX, positionY, width, height,
                           label=None):
        self.addControl("com.sun.star.awt.UncontrolFixedTextModel",
                         ctrlName, positionX, positionY, width, height,
                         label=label)
           
    #--------------------------------------------------
    #   Add Controls to dialog
    #--------------------------------------------------

    def addControl(self, ctrlServiceName,
                        ctrlName, positionX, positionY, width, height,
                        label=None, tabIndex=None):
        controlModel = self.model.createInstance(ctrlServiceName)
        self.model.insertByName(ctrlName, controlModel)

        # if negative coordinates are given for X or Y position,
        #  then make that coordinate be relative to the right/bottom
        #  edge of the dialog box instead of to the left/top.
        if positionX < 0: positionX = self.model.Width  + positionX - width
        if positionY < 0: positionY = self.model.Height + positionY - height
        controlModel.PositionX = positionX
        controlModel.PositionY = positionY
        controlModel.Width = width
        controlModel.Height = height
        controlModel.Name = ctrlName
       
        if label is not None:
            controlModel.Label = label

        if tabIndex is not None:
            controlModel.TabIndex = tabIndex

    #--------------------------------------------------
    #   Access controls and control models
    #--------------------------------------------------

    def getControl(self, ctrlName):
        """Get the control (not its model) for a particular control name.
        The control returned includes the service com.sun.star.awt.Uncontrol,
         and another control-specific service which inherits from it.
        """
        control = self.dialogControl.getControl(ctrlName)
        return control

    def getControlModel(self, ctrlName):
        """Get the control model (not the control) for a particular control name.
        The model returned includes the service UncontrolModel,
         and another control-specific service which inherits from it.
        """
        control = self.getControl(ctrlName)
        controlModel = control.getModel()
        return controlModel


    #--------------------------------------------------
    #   Adjust properties of control models
    #--------------------------------------------------

    def setControlModelProperty(self, ctrlName, propertyName, value):
        """Set the value of a property of a control's model.
        This affects the control model, not the control.
        """
        controlModel = self.getControlModel(ctrlName)
        controlModel.setPropertyValue(propertyName, value)

    def getControlModelProperty(self, ctrlName, propertyName):
        """Get the value of a property of a control's model.
        This affects the control model, not the control.
        """
        controlModel = self.getControlModel(ctrlName)
        return controlModel.getPropertyValue(propertyName)


    #--------------------------------------------------
    #   Sugar coated property adjustments to control models.
    #--------------------------------------------------

    def setEnabled(self, ctrlName, enabled=True):
        """Supported controls...
            UncontrolButtonModel
            UncontrolCheckBoxModel
        """
        self.setControlModelProperty(ctrlName, "Enabled", enabled)

    def getEnabled(self, ctrlName):
        """Supported controls...
            UncontrolButtonModel
            UncontrolCheckBoxModel
        """
        return self.getControlModelProperty(ctrlName, "Enabled")

    def setState(self, ctrlName, state):
        """Supported controls...
            UncontrolButtonModel
            UncontrolCheckBoxModel
        """
        self.setControlModelProperty(ctrlName, "State", state)

    def getState(self, ctrlName):
        """Supported controls...
            UncontrolButtonModel
            UncontrolCheckBoxModel
        """
        return self.getControlModelProperty(ctrlName, "State")

    def setLabel(self, ctrlName, label):
        """Supported controls...
            UncontrolButtonModel
            UncontrolCheckBoxModel
        """
        self.setControlModelProperty(ctrlName, "Label", label)

    def getLabel(self, ctrlName):
        """Supported controls...
            UncontrolButtonModel
            UncontrolCheckBoxModel
        """
        return self.getControlModelProperty(ctrlName, "Label")

    def setHelpText(self, ctrlName, helpText):
        """Supported controls...
            UncontrolButtonModel
            UncontrolCheckBoxModel
        """
        self.setControlModelProperty(ctrlName, "HelpText", helpText)

    def getHelpText(self, ctrlName):
        """Supported controls...
            UncontrolButtonModel
            UncontrolCheckBoxModel
        """
        return self.getControlModelProperty(ctrlName, "HelpText")


    #--------------------------------------------------
    #   Adjust controls (not models)
    #--------------------------------------------------

    # The following apply to all controls which are a
    #   com.sun.star.awt.Uncontrol

    def setDesignMode(self, ctrlName, designMode=True):
        self.getControl(ctrlName).setDesignMode(designMode)

    def isDesignMode(self, ctrlName, designMode=True):
        return self.getControl(ctrlName).isDesignMode()
 
    def isTransparent(self, ctrlName, designMode=True):
        return self.getControl(ctrlName).isTransparent()
     

    # The following apply to all controls which are a
    #   com.sun.star.awt.UncontrolDialogElement

    def setPosition(self, ctrlName, positionX, positionY):
        self.setControlModelProperty(ctrlName, "PositionX", positionX)
        self.setControlModelProperty(ctrlName, "PositionY", positionY)
    def setPositionX(self, ctrlName, positionX):
        self.setControlModelProperty(ctrlName, "PositionX", positionX)
    def setPositionY(self, ctrlName, positionY):
        self.setControlModelProperty(ctrlName, "PositionY", positionY)
    def getPositionX(self, ctrlName):
        return self.getControlModelProperty(ctrlName, "PositionX")
    def getPositionY(self, ctrlName):
        return self.getControlModelProperty(ctrlName, "PositionY")

    def setSize(self, ctrlName, width, height):
        self.setControlModelProperty(ctrlName, "Width", width)
        self.setControlModelProperty(ctrlName, "Height", height)
    def setWidth(self, ctrlName, width):
        self.setControlModelProperty(ctrlName, "Width", width)
    def setHeight(self, ctrlName, height):
        self.setControlModelProperty(ctrlName, "Height", height)
    def getWidth(self, ctrlName):
        return self.getControlModelProperty(ctrlName, "Width")
    def getHeight(self, ctrlName):
        return self.getControlModelProperty(ctrlName, "Height")

    def setTabIndex(self, ctrlName, width, tabIndex):
        self.setControlModelProperty(ctrlName, "TabIndex", tabIndex)
    def getTabIndex(self, ctrlName):
        return self.getControlModelProperty(ctrlName, "TabIndex")

    def setStep(self, ctrlName, width, step):
        self.setControlModelProperty(ctrlName, "Step", step)
    def getStep(self, ctrlName):
        return self.getControlModelProperty(ctrlName, "Step")

    def setTag(self, ctrlName, width, tag):
        self.setControlModelProperty(ctrlName, "Tag", tag)
    def getTag(self, ctrlName):
        return self.getControlModelProperty(ctrlName, "Tag")


    #--------------------------------------------------
    #   Add listeners to controls.
    #--------------------------------------------------

    # This applies to...
    #   UncontrolButton
    def addActionListenerProc(self, ctrlName, actionListenerProc):
        """Create an com.sun.star.awt.XActionListener object and add it to a control.
        A listener object is created which will call the python procedure actionListenerProc.
        The actionListenerProc can be either a method or a global procedure.
        The following controls support XActionListener:
            UncontrolButton
        """
        control = self.getControl(ctrlName)
        actionListener = ActionListenerProcAdapter(actionListenerProc)
        control.addActionListener(actionListener)

    # This applies to...
    #   UncontrolCheckBox
    def addItemListenerProc(self, ctrlName, itemListenerProc):
        """Create an com.sun.star.awt.XItemListener object and add it to a control.
        A listener object is created which will call the python procedure itemListenerProc.
        The itemListenerProc can be either a method or a global procedure.
        The following controls support XActionListener:
            UncontrolCheckBox
        """
        control = self.getControl(ctrlName)
        actionListener = ItemListenerProcAdapter(itemListenerProc)
        control.addItemListener(actionListener)

    #--------------------------------------------------
    #   Display the modal dialog.
    #--------------------------------------------------

    def doModalDialog(self):
        """Display the dialog as a modal dialog."""
        self.dialogControl.setVisible(True)
        self.dialogControl.execute()

    def endExecute(self):
        """Call this from within one of the listeners to end the modal dialog.
        For instance, the listener on your OK or Cancel button would call this to end the dialog.
        """
        self.dialogControl.endExecute()




#--------------------------------------------------
# Example of Dialog box built by subclassing the DBModalDialog class.

class Test1Dialog(DBModalDialog):
    def __init__(self):
        DBModalDialog.__init__(self)
        self.setDialogPosition(60, 50)
        self.setDialogSize(150, 80)
        self.setDialogTitle("My Test1 Dialog")
        self.addButton("btnOK", -10, -10, 30, 14, "OK",
                        actionListenerProc = self.btnOK_clicked)
        self.addButton("btnCancel", -50, -10, 30, 14, "Cancel",
                        actionListenerProc = self.btnCancel_clicked)
        self.okClicks = 0
        self.cancelClicks = 0

    # Called when the OK button is clicked.
    def btnOK_clicked(self, event):
        self.okClicks += 1

    # Called when the Cancel button is clicked.
    def btnCancel_clicked(self, event):
        self.cancelClicks += 1

def Test1():
    testDialog =  Test1Dialog()

    # Display dialog box.
    # This does not return until the dialog box is dismissed.
    testDialog.doModalDialog()
   
    # Print out the global button click counters.
    print testDialog.cancelClicks, testDialog.okClicks



#--------------------------------------------------
# Example of modal creating a dialog box without subclassing DBModalDialog.

# Global vars to keep track of button clicks.
okClicks = 0
cancelClicks = 0
# Global procs, called as event listeners on button clicks.
def OKClicked(event):
    global okClicks
    okClicks += 1
def CancelClicked(event):
    global cancelClicks
    cancelClicks += 1

# Create a modal dialog box without subclassing DBModalDialog.
def Test2():
    testDialog = DBModalDialog(60, 50, 150, 80, "My Test2 Dialog")
    testDialog.addButton("btnOK", -10, -10, 30, 14, "OK")
    testDialog.addButton("btnCancel", -50, -10, 30, 14, "Cancel")
    testDialog.addFixedText("lbl01", 10, 10, 30, 14, "Test1")

    # Install global event listener procs.
    # Use the addActionListenerProc() routine instead of supplying the event
    #  listener to the addButton() as in first example.
    testDialog.addActionListenerProc("btnOK", OKClicked)
    testDialog.addActionListenerProc("btnCancel", CancelClicked)

    # Display dialog box.
    # This does not return until the dialog box is dismissed.
    testDialog.doModalDialog()

    # Print out the global button click counters.
    print cancelClicks, okClicks




#--------------------------------------------------
# Example of Dialog box built by subclassing the DBModalDialog class.

class ModalDoggieKittyMonkeyDialog(DBModalDialog):
    def __init__(self):       
        self.numDoggies = 0
        self.numKitties = 0
        self.numMonkeys = 0
        self.tails = False
        self.okay = False

        DBModalDialog.__init__(self, 60, 50, 200, 90, "Doggie/Kitty/Monkey Dialog")

        # Add an OK and a Cancel button.
        # Both buttons share an action listener named "self.btnOkOrCancel_clicked".
        self.addButton("btnOK", -10, -10, 50, 14, "OK",
                        actionListenerProc = self.btnOkOrCancel_clicked)
        self.addButton("btnCancel", -10 - 50 - 10, -10, 50, 14, "Cancel",
                        actionListenerProc = self.btnOkOrCancel_clicked)

        # Add three buttons.
        self.addButton("btnDoggie", 5, 10, 50, 14, "Add Doggie",
                        actionListenerProc = self.btnDoggie_Clicked)
        self.addButton("btnKitty", 5, 30, 50, 14, "Add Kitty",
                        actionListenerProc = self.btnKitty_Clicked)
        self.addButton("btnMonkey", 5, 50, 50, 14, "Add Monkey",
                        actionListenerProc = self.btnMonkey_Clicked)

        # Add a label to the dialog.
        self.addFixedText("lbl1", 60, 10, 100, 14, "Add some doggies, kitties, and monkeys.")

        # Add a checkbox to the dialog.
        self.addCheckBox("chkTails", 60, 30, 50, 14, "With tails",
                          itemListenerProc = self.chkTails_changed)

    def btnOkOrCancel_clicked(self, event):
        """Called when the OK or Cancel button is clicked."""
        if event.Source.getModel().Name == "btnOK":
            self.okay = True
        self.endExecute()

    def btnDoggie_Clicked(self, event):
        """Called with the Doggie button is clicked."""
        self.numDoggies += 1

    def btnKitty_Clicked(self, event):
        """Called with the Kitty button is clicked."""
        self.numKitties += 1

    def btnMonkey_Clicked(self, event):
        """Called with the Monkey button is clicked."""
        self.numMonkeys += 1

    def chkTails_changed(self, event):
        """Called when the Tails checkbox is clicked."""
        self.tails = self.getState("chkTails")


def Test3():
    testDialog = ModalDoggieKittyMonkeyDialog()
    testDialog.doModalDialog()
   
    # Print out the global button click counters.
    print testDialog.numDoggies, testDialog.numKitties, testDialog.numMonkeys
    print "okay:", testDialog.okay,
    print "tails:", testDialog.tails, testDialog.getState("chkTails")





#>>> import Danny.OOo.DialogLib
#>>> reload(Danny.OOo.DialogLib); from Danny.OOo.DialogLib import *
