#!/usr/bin/python

"""
Extends the base QToolButton class to support popup widgets.
"""

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software'
__license__         = 'LGPL'

# maintanence information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

from projexui.qt          import Signal
from projexui.qt.QtCore   import QPoint
from projexui.qt.QtGui    import QToolButton,\
                                 QDialogButtonBox

from projexui.widgets.xpopupwidget  import XPopupWidget

class XPopupButton(QToolButton):
    popupAboutToShow = Signal()
    popupAccepted    = Signal()
    popupRejected    = Signal()
    popupReset       = Signal()
    
    Anchor = XPopupWidget.Anchor
    
    def __init__( self, parent, buttons = None ):
        super(XPopupButton, self).__init__(parent)
        
        # define custom options
        if ( buttons is None ):
            buttons  = QDialogButtonBox.Reset
            buttons |= QDialogButtonBox.Save
            buttons |= QDialogButtonBox.Cancel
        
        self._popupWidget   = XPopupWidget(self, buttons)
        self._defaultAnchor = 0
        
        self.setEnabled(False)
        
        # create connections
        self.clicked.connect(self.showPopup)
        self.triggered.connect(self.showPopupOnAction)
        
        self._popupWidget.accepted.connect(self.popupAccepted)
        self._popupWidget.rejected.connect(self.popupRejected)
        self._popupWidget.resetRequested.connect(self.popupReset)
    
    def centralWidget( self ):
        """
        Returns the central widget from this tool button
        """
        return self._popupWidget.centralWidget()
    
    def defaultAnchor( self ):
        """
        Returns the default anchor for this popup widget.
        
        :return     <XPopupWidget.Anchor>
        """
        return self._defaultAnchor
    
    def popupWidget( self ):
        """
        Returns the popup widget for this button.
        
        :return     <XPopupWidget>
        """
        return self._popupWidget
    
    def setCentralWidget( self, widget ):
        """
        Sets the central widget for this button.
        
        :param      widget | <QWidget>
        """
        self.setEnabled(widget is not None)
        self._popupWidget.setCentralWidget(widget)
    
    def setDefaultAnchor( self, anchor ):
        """
        Sets the default anchor for the popup on this button.
        
        :param      anchor | <XPopupWidget.Anchor>
        """
        self._defaultAnchor = anchor
    
    def showPopupOnAction( self, action ):
        """
        Shows the popup if the action is the current default action.
        
        :param      action | <QAction>
        """
        if ( action == self.defaultAction() ):
            self.showPopup()
    
    def showPopup( self ):
        """
        Shows the popup for this button.
        """
        anchor = self.defaultAnchor()
        if ( anchor ):
            self.popupWidget().setAnchor(anchor)
        else:
            anchor = self.popupWidget().anchor()
        
        if ( anchor & (XPopupWidget.Anchor.BottomLeft |
                       XPopupWidget.Anchor.BottomCenter |
                       XPopupWidget.Anchor.BottomRight) ):
            pos = QPoint(self.width() / 2, 0)
        else:
            pos = QPoint(self.width() / 2, self.height())
        
        pos = self.mapToGlobal(pos)
        
        if ( not self.signalsBlocked() ):
            self.popupAboutToShow.emit()
        self._popupWidget.popup(pos)

__designer_plugins__ = [XPopupButton]