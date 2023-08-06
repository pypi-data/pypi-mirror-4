#!/usr/bin python

""" Defines a more robust tab widget. """

# define authorship information
__authors__     = ['Eric Hulser']
__author__      = ','.join(__authors__)
__credits__     = []
__copyright__   = 'Copyright (c) 2011, Projex Software'

# maintanence information
__maintainer__  = 'Projex Software'
__email__       = 'team@projexsoftware.com'

from projexui.qt import Signal
from projexui.qt.QtCore   import QPoint,\
                                 QSize,\
                                 Qt
                           
from projexui.qt.QtGui    import QApplication,\
                                 QCursor, \
                                 QIcon, \
                                 QTabWidget,\
                                 QTabBar,\
                                 QToolButton

from projexui       import resources

class XTabBar(QTabBar):
    def __init__( self, parent ):
        super(XTabBar, self).__init__(parent)
        
        # update the font
        font = self.font()
        font.setPointSize(8)
        self.setFont(font)
        
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # set custom properties
        self._buttonSize = QSize(10, 10)
    
    def buttonSize( self ):
        """
        Returns the button size that will be used for this tab bar's buttons.
        
        :return     <QSize>
        """
        return self._buttonSize
    
    def dragEnterEvent( self, event ):
        self.parent().eventFilter(self, event)
        super(XTabBar, self).dragEnterEvent(event)
    
    def dragMoveEvent( self, event ):
        self.parent().eventFilter(self, event)
        super(XTabBar, self).dragMoveEvent(event)
    
    def dropEvent( self, event ):
        self.parent().eventFilter(self, event)
        super(XTabBar, self).dropEvent(event)
    
    def setButtonSize( self, size ):
        """
        Sets the button size that will be used for the tab page buttons.
        
        :param      size | <QSize>
        """
        self._buttonSize = size
    
    def tabInserted( self, index ):
        """
        Overloads the tab inserted method to update the size for the close \
        buttons.
        
        :param      index | <int>
        """
        super(XTabBar, self).tabInserted(index)
        
        size    = self.buttonSize()
        
        # update the right side button
        for side in (self.LeftSide, self.RightSide):
            button  = self.tabButton(index, side)
            if ( not button ):
                continue
                
            button.setFixedWidth(  size.width() )
            button.setFixedHeight( size.height() )

#------------------------------------------------------------------------------

class XTabWidget(QTabWidget):
    addRequested     = Signal(QPoint)
    optionsRequested = Signal(QPoint)
    
    def __init__( self, *args ):
        super(XTabWidget, self).__init__(*args)
        
        # create the tab bar
        self.setTabBar( XTabBar(self) )
        
        # create the add button
        self._addButton = QToolButton(self)
        self._addButton.setIcon(QIcon(resources.find('img/add_tab.png')))
        self._addButton.setFixedSize( 18, 18 )
        self._addButton.setAutoRaise(True)
        
        # create the option button
        self._optionsButton = QToolButton(self)
        self._optionsButton.setIcon(QIcon(resources.find('img/arrow.png')))
        self._optionsButton.setFixedSize( 18, 18 )
        self._optionsButton.setAutoRaise(True)
        
        # create connection
        self._optionsButton.clicked.connect( self.emitOptionsRequested )
        self._addButton.clicked.connect(     self.emitAddRequested )
    
    
    def __nonzero__( self ):
        """
        At somepoint, QTabWidget's nonzero became linked to whether it had
        children vs. whether it was none.  This returns the original
        functionality.
        """
        return self is not None
    
    
    def adjustButtons( self ):
        """
        Updates the position of the buttons based on the current geometry.
        """
        tabbar = self.tabBar()
        tabbar.adjustSize()
        
        self._addButton.move( tabbar.width() + 2, 1 )
        self._optionsButton.move( self.width() - 20, 1 )
        
    def addButton( self ):
        """
        Returns the add button linked with this tab widget.
        
        :return     <QToolButton>
        """
        return self._addButton
    
    def emitAddRequested( self, point = None ):
        """
        Emitted when the option menu button is clicked provided the signals \
        are not being blocked for this widget.
        
        :param      point | <QPoint>
        """
        if ( self.signalsBlocked() ):
            return
        
        if ( not point ):
            point = QCursor.pos()
        
        self.addRequested.emit(point)
    
    def emitOptionsRequested( self, point = None ):
        """
        Emitted when the option menu button is clicked provided the signals \
        are not being blocked for this widget.
        
        :param      point | <QPoint>
        """
        if ( self.signalsBlocked() ):
            return
        
        if ( not point ):
            point = QCursor.pos()
        
        self.optionsRequested.emit(point)
    
    def optionsButton( self ):
        """
        Returns the options button linked with this tab widget.
        
        :return     <QToolButton>
        """
        return self._optionsButton
    
    def resizeEvent( self, event ):
        """
        Updates the position of the additional buttons when this widget \
        resizes.
        
        :param      event | <QResizeEvet>
        """
        super(XTabWidget, self).resizeEvent( event )
        self.adjustButtons()
    
    def setShowAddButton( self, state ):
        """
        Sets whether or not the add button is visible.
        
        :param      state | <bool>
        """
        self._addButton.setVisible(state)
    
    def setShowOptionsButton( self, state ):
        """
        Sets whether or not the option button is visible.
        
        :param          state   | <bool>
        """
        self._optionsButton.setVisible(state)
    
    def setVisible( self, state ):
        """
        Overloads the base setVisible method to update the button position.
        
        :param      state | <bool>
        """
        super(XTabWidget, self).setVisible(state)
        if ( state ):
            self.adjustButtons()
    
    def showAddButton( self ):
        """
        Returns whether or not the add button is visible.
        
        :return     <bool>
        """
        return self._addButton.isVisible()
    
    def showOptionsButton( self ):
        """
        Returns whether or not the option button should be visible.
        
        :return     <bool>
        """
        return self._optionsButton.isVisible()
    
    def tabInserted( self, index ):
        """
        Overloads the tabInserted method to properly update the buttons for \
        this tab.
        
        :param      index | <int>
        """
        super(XTabWidget, self).tabInserted(index)
        self.adjustButtons()
    
    def tabRemoved( self, index ):
        """
        Overloads the tabRemoved method to properly update the buttons for \
        this tab.
        
        :param      index | <int>
        """
        super(XTabWidget, self).tabRemoved(index)
        self.adjustButtons()