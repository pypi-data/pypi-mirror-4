#!/usr/bin/python

""" Defines a generic widget to handle popup controls. """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2012, Projex Software'
__license__         = 'LGPL'

# maintenance information
__maintainer__      = 'Projex Software'
__email__           = 'team@projexsoftware.com'

#------------------------------------------------------------------------------

import weakref

from projexui.qt import Signal
from projexui.qt.QtCore   import QSize,\
                                 Qt
                           
from projexui.qt.QtGui    import QAbstractButton,\
                                 QBitmap,\
                                 QColor,\
                                 QCursor,\
                                 QHBoxLayout,\
                                 QIcon,\
                                 QPainter,\
                                 QPainterPath,\
                                 QPen,\
                                 QScrollArea,\
                                 QSizeGrip,\
                                 QVBoxLayout,\
                                 QToolButton,\
                                 QWidget,\
                                 QCursor,\
                                 QPalette,\
                                 QSizePolicy,\
                                 QDialogButtonBox,\
                                 QLabel,\
                                 QApplication,\
                                 QGraphicsDropShadowEffect

from projex.enum import enum
from projex.decorators import deprecatedmethod

import projexui.resources

class XPopupWidget(QWidget):
    """ """
    Direction = enum('North', 'South', 'East', 'West')
    Mode      = enum('Popup', 'Dialog', 'ToolTip')
    Anchor    = enum('TopLeft',
                     'TopCenter',
                     'TopRight',
                     'LeftTop',
                     'LeftCenter',
                     'LeftBottom',
                     'RightTop',
                     'RightCenter',
                     'RightBottom',
                     'BottomLeft',
                     'BottomCenter',
                     'BottomRight')
    
    aboutToShow     = Signal()
    accepted        = Signal()
    rejected        = Signal()
    resetRequested  = Signal()
    buttonClicked   = Signal(QAbstractButton)
    
    _toolTipWidget  = {}
    
    def __init__( self, parent = None, buttons = None ):
        super(XPopupWidget, self).__init__( parent )
        
        # define custom properties
        self._anchor                = XPopupWidget.Anchor.TopCenter
        self._autoCalculateAnchor   = False
        self._autoCloseOnAccept     = True
        self._autoCloseOnReject     = True
        self._currentMode           = None
        
        # define controls
        self._resizable     = True
        self._popupPadding  = 10
        self._dialogButton  = QToolButton(self)
        self._closeButton   = QToolButton(self)
        self._scrollArea    = QScrollArea(self)
        self._sizeGrip      = QSizeGrip(self)
        self._sizeGrip.setFixedWidth(12)
        self._sizeGrip.setFixedHeight(12)
        
        if ( buttons is None ):
            buttons = QDialogButtonBox.NoButton
        
        self._buttonBox     = QDialogButtonBox(buttons, Qt.Horizontal, self)
        self._buttonBox.setContentsMargins(3, 0, 3, 9)
        
        self._scrollArea.setWidgetResizable(True)
        self._scrollArea.setFrameShape(QScrollArea.NoFrame)
        self._scrollArea.setSizePolicy(QSizePolicy.Expanding,
                                       QSizePolicy.Expanding)
        
        palette = self.palette()
        self._scrollArea.setPalette(palette)
        
        self._dialogButton.setToolTip('Popout to Dialog')
        self._closeButton.setToolTip('Close Popup')
        
        for btn in (self._dialogButton, self._closeButton):
            btn.setAutoRaise(True)
            btn.setIconSize(QSize(14, 14))
            btn.setMaximumSize(16, 16)
        
        # setup the icons
        icon = QIcon(projexui.resources.find('img/dialog.png'))
        self._dialogButton.setIcon(icon)
        
        icon = QIcon(projexui.resources.find('img/close.png'))
        self._closeButton.setIcon(icon)
        
        # define the ui
        hlayout = QHBoxLayout()
        hlayout.setSpacing(0)
        hlayout.addStretch(1)
        hlayout.addWidget(self._dialogButton)
        hlayout.addWidget(self._closeButton)
        hlayout.setContentsMargins(0, 0, 0, 0)
        
        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(self._buttonBox)
        hlayout2.setContentsMargins(0, 0, 3, 0)
        
        vlayout = QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addWidget(self._scrollArea)
        vlayout.addLayout(hlayout2)
        vlayout.setContentsMargins(3, 0, 3, 0)
        vlayout.setSpacing(0)
        
        self.setLayout(vlayout)
        
        # set default properties
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.Button)
        self.setWindowTitle('Popup')
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCurrentMode(XPopupWidget.Mode.Popup)
        
        if ( parent ):
            parent.window().installEventFilter(self)
        
        # create connections
        self._dialogButton.clicked.connect(self.setDialogMode)
        self._closeButton.clicked.connect(self.reject)
        self._buttonBox.accepted.connect(self.accept)
        self._buttonBox.rejected.connect(self.reject)
        self._buttonBox.clicked.connect(self.handleButtonClick)
    
    def addButton(self, button, role=QDialogButtonBox.ActionRole):
        """
        Adds a custom button to the button box for this popup widget.
        
        :param      button | <QAbstractButton> || <str>
        
        :return     <button> || None (based on if a button or string was given)
        """
        return self._buttonBox.addButton(button, role)
    
    def adjustContentsMargins( self ):
        """
        Adjusts the contents for this widget based on the anchor and \
        mode.
        """
        anchor = self.anchor()
        mode   = self.currentMode()
        
        # margins for a dialog
        if ( mode == XPopupWidget.Mode.Dialog ):
            self.setContentsMargins(0, 0, 0, 0)
        
        # margins for a top anchor point
        elif ( anchor & (XPopupWidget.Anchor.TopLeft |
                         XPopupWidget.Anchor.TopCenter |
                         XPopupWidget.Anchor.TopRight) ):
            self.setContentsMargins(0, self.popupPadding() + 5, 0, 0)
        
        # margins for a bottom anchor point
        elif ( anchor & (XPopupWidget.Anchor.BottomLeft |
                         XPopupWidget.Anchor.BottomCenter |
                         XPopupWidget.Anchor.BottomRight) ):
            self.setContentsMargins(0, 0, 0, self.popupPadding())
        
        # margins for a left anchor point
        elif ( anchor & (XPopupWidget.Anchor.LeftTop |
                         XPopupWidget.Anchor.LeftCenter |
                         XPopupWidget.Anchor.LeftBottom) ):
            self.setContentsMargins(self.popupPadding(), 0, 0, 0)
        
        # margins for a right anchor point
        else:
            self.setContentsMargins(0, 0, self.popupPadding(), 0)
        
        self.adjustMask()
    
    def adjustMask( self ):
        """
        Updates the alpha mask for this popup widget.
        """
        if ( self.currentMode() == XPopupWidget.Mode.Dialog ):
            self.clearMask()
            return
        
        path = self.borderPath()
        bitmap = QBitmap(self.width(), self.height())
        bitmap.fill(QColor('white'))
        
        painter = QPainter()
        painter.begin(bitmap)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor('black'))
        pen.setWidthF(1.5)
        painter.setPen(pen)
        painter.setBrush(QColor('black'))
        painter.drawPath(path)
        painter.end()
        
        self.setMask(bitmap)
    
    def adjustSize( self ):
        """
        Adjusts the size of this popup to best fit the new widget size.
        """
        widget = self.centralWidget()
        if ( not widget ):
            super(XPopupWidget, self).adjustSize()
            return
        
        widget.adjustSize()
        hint = widget.minimumSizeHint()
        size = widget.minimumSize()
        
        width  = max(size.width(),  hint.width())
        height = max(size.height(), hint.height())
        
        if ( self.currentMode() != self.Mode.ToolTip ):
            width  += 25
            height += 95
        else:
            width  += 15
            height += 15
        
        curr_w = self.width()
        curr_h = self.height()
        
        # determine if we need to move based on our anchor
        anchor = self.anchor()
        if ( anchor & (self.Anchor.LeftBottom | self.Anchor.RightBottom | \
                       self.Anchor.BottomLeft | self.Anchor.BottomCenter | \
                       self.Anchor.BottomRight) ):
            delta_y = height - curr_h
        
        elif ( anchor & (self.Anchor.LeftCenter | self.Anchor.RightCenter) ):
            delta_y = (height - curr_h) / 2
        
        else:
            delta_y = 0
        
        if ( anchor & (self.Anchor.RightTop | self.Anchor.RightCenter | \
                       self.Anchor.RightTop | self.Anchor.TopRight) ):
            delta_x = width - curr_w
        
        elif ( anchor & (self.Anchor.TopCenter | self.Anchor.BottomCenter) ):
            delta_x = (width - curr_w) / 2
        
        else:
            delta_x = 0
        
        self.setMinimumSize(width, height)
        self.resize(width, height)
        
        pos = self.pos()
        pos.setX(pos.x() - delta_x)
        pos.setY(pos.y() - delta_y)
        
        self.move(pos)
    
    def accept( self ):
        """
        Emits the accepted signal and closes the popup.
        """
        if ( not self.signalsBlocked() ):
            self.accepted.emit()
        
        if ( self.autoCloseOnAccept() ):
            self.close()
    
    def anchor( self ):
        """
        Returns the anchor point for this popup widget.
        
        :return     <XPopupWidget.Anchor>
        """
        return self._anchor
    
    def autoCalculateAnchor( self ):
        """
        Returns whether or not this popup should calculate the anchor point
        on popup based on the parent widget and the popup point.
        
        :return     <bool>
        """
        return self._autoCalculateAnchor
    
    def autoCloseOnAccept( self ):
        """
        Returns whether or not this popup widget manages its own close on accept
        behavior.
        
        :return     <bool>
        """
        return self._autoCloseOnAccept
    
    def autoCloseOnReject( self ):
        """
        Returns whether or not this popup widget manages its own close on reject
        behavior.
        
        :return     <bool>
        """
        return self._autoCloseOnReject
    
    def borderPath(self):
        """
        Returns the border path that will be drawn for this widget.
        
        :return     <QPainterPath>
        """
        
        path = QPainterPath()
        
        x = 1
        y = 1
        w = self.width() - 2
        h = self.height() - 2
        pad = self.popupPadding()
        anchor = self.anchor()
        
        # create a path for a top-center based popup
        if ( anchor == XPopupWidget.Anchor.TopCenter ):
            path.moveTo(x, y + pad)
            path.lineTo(x + ((w/2) - pad), y + pad)
            path.lineTo(x + (w/2), y)
            path.lineTo(x + ((w/2) + pad), y + pad)
            path.lineTo(x + w, y + pad)
            path.lineTo(x + w, y + h)
            path.lineTo(x, y + h)
            path.lineTo(x, y + pad)
        
        # create a path for a top-left based popup
        elif ( anchor == XPopupWidget.Anchor.TopLeft ):
            path.moveTo(x, y + pad)
            path.lineTo(x + pad, y)
            path.lineTo(x + 2 * pad, y + pad)
            path.lineTo(x + w, y + pad)
            path.lineTo(x + w, y + h)
            path.lineTo(x, y + h)
            path.lineTo(x, y + pad)
        
        # create a path for a top-right based popup
        elif ( anchor == XPopupWidget.Anchor.TopRight ):
            path.moveTo(x, y + pad)
            path.lineTo(x + w - 2 * pad, y + pad)
            path.lineTo(x + w - pad, y)
            path.lineTo(x + w, y + pad)
            path.lineTo(x + w, y + h)
            path.lineTo(x, y + h)
            path.lineTo(x, y + pad)
        
        # create a path for a bottom-left based popup
        elif ( anchor == XPopupWidget.Anchor.BottomLeft ):
            path.moveTo(x, y)
            path.lineTo(x + w, y)
            path.lineTo(x + w, y + h - pad)
            path.lineTo(x + 2 * pad, y + h - pad)
            path.lineTo(x + pad, y + h)
            path.lineTo(x, y + h - pad)
            path.lineTo(x, y)
        
        # create a path for a south based popup
        elif ( anchor == XPopupWidget.Anchor.BottomCenter ):
            path.moveTo(x, y)
            path.lineTo(x + w, y)
            path.lineTo(x + w, y + h - pad)
            path.lineTo(x + ((w/2) + pad), y + h - pad)
            path.lineTo(x + (w/2), y + h)
            path.lineTo(x + ((w/2) - pad), y + h - pad)
            path.lineTo(x, y + h - pad)
            path.lineTo(x, y)
        
        # create a path for a bottom-right based popup
        elif ( anchor == XPopupWidget.Anchor.BottomRight ):
            path.moveTo(x, y)
            path.lineTo(x + w, y)
            path.lineTo(x + w, y + h - pad)
            path.lineTo(x + w - pad, y + h)
            path.lineTo(x + w - 2 * pad, y + h - pad)
            path.lineTo(x, y + h - pad)
            path.lineTo(x, y)
        
        # create a path for a right-top based popup
        elif ( anchor == XPopupWidget.Anchor.RightTop ):
            path.moveTo(x, y)
            path.lineTo(x + w - pad, y)
            path.lineTo(x + w, y + pad)
            path.lineTo(x + w - pad, y + 2 * pad)
            path.lineTo(x + w - pad, y + h)
            path.lineTo(x, y + h)
            path.lineTo(x, y)
        
        # create a path for a right-center based popup
        elif ( anchor == XPopupWidget.Anchor.RightCenter ):
            path.moveTo(x, y)
            path.lineTo(x + w - pad, y)
            path.lineTo(x + w - pad, y + ((h/2) - pad))
            path.lineTo(x + w, y + (h/2))
            path.lineTo(x + w - pad, y + ((h/2) + pad))
            path.lineTo(x + w - pad, y + h)
            path.lineTo(x, y + h)
            path.lineTo(x, y)
        
        # create a path for a right-bottom based popup
        elif ( anchor == XPopupWidget.Anchor.RightBottom ):
            path.moveTo(x, y)
            path.lineTo(x + w - pad, y)
            path.lineTo(x + w - pad, y + h - 2 * pad)
            path.lineTo(x + w, y + h - pad)
            path.lineTo(x + w - pad, y + h)
            path.lineTo(x, y + h)
            path.lineTo(x, y)
        
        # create a path for a left-top based popup
        elif ( anchor == XPopupWidget.Anchor.LeftTop ):
            path.moveTo(x + pad, y)
            path.lineTo(x + w, y)
            path.lineTo(x + w, y + h)
            path.lineTo(x + pad, y + h)
            path.lineTo(x + pad, y + 2 * pad)
            path.lineTo(x, y + pad)
            path.lineTo(x + pad, y)
        
        # create a path for an left-center based popup
        elif ( anchor == XPopupWidget.Anchor.LeftCenter ):
            path.moveTo(x + pad, y)
            path.lineTo(x + w, y)
            path.lineTo(x + w, y + h)
            path.lineTo(x + pad, y + h)
            path.lineTo(x + pad, y + ((h/2) + pad))
            path.lineTo(x, y + (h/2))
            path.lineTo(x + pad, y + ((h/2) - pad))
            path.lineTo(x + pad, y)
        
        # create a path for a left-bottom based popup
        elif ( anchor == XPopupWidget.Anchor.LeftBottom ):
            path.moveTo(x + pad, y)
            path.lineTo(x + w, y)
            path.lineTo(x + w, y + h)
            path.lineTo(x + pad, y + h)
            path.lineTo(x, y + h - pad)
            path.lineTo(x + pad, y + h - 2 * pad)
            path.lineTo(x + pad, y)
        
        return path
    
    def buttonBox( self ):
        """
        Returns the button box that is used to control this popup widget.
        
        :return     <QDialogButtonBox>
        """
        return self._buttonBox
    
    def centralWidget( self ):
        """
        Returns the central widget that is being used by this popup.
        
        :return     <QWidget>
        """
        return self._scrollArea.widget()
    
    def close( self ):
        """
        Closes the popup widget and central widget.
        """
        widget = self.centralWidget()
        if ( widget and not widget.close() ):
            return
            
        super(XPopupWidget, self).close()
    
    def currentMode( self ):
        """
        Returns the current mode for this widget.
        
        :return     <XPopupWidget.Mode>
        """
        return self._currentMode
    
    @deprecatedmethod('XPopupWidget', 
                      'Direction is no longer used, use anchor instead')
    def direction( self ):
        """
        Returns the current direction parameter for this widget.
        
        :return     <XPopupWidget.Direction>
        """
        anchor = self.anchor()
        if ( anchor & (XPopupWidget.Anchor.TopLeft |
                       XPopupWidget.Anchor.TopCenter |
                       XPopupWidget.Anchor.TopRight) ):
            return XPopupWidget.Direction.North
        
        elif ( anchor & (XPopupWidget.Anchor.BottomLeft |
                         XPopupWidget.Anchor.BottomCenter |
                         XPopupWidget.Anchor.BottomRight) ):
            return XPopupWidget.Direction.South
        
        elif ( anchor & (XPopupWidget.Anchor.LeftTop |
                         XPopupWidget.Anchor.LeftCenter |
                         XPopupWidget.Anchor.LeftBottom) ):
            return XPopupWidget.Direction.East
        
        else:
            return XPopupWidget.Direction.West
    
    def eventFilter( self, object, event ):
        """
        Processes when the window is moving to update the position for the
        popup if in popup mode.
        
        :param      object | <QObject>
                    event  | <QEvent>
        """
        if ( event.type() == event.Move and \
             self.currentMode() != self.Mode.Dialog ):
            deltaPos = event.pos() - event.oldPos()
            self.move(self.pos() + deltaPos)
            return False
        
        if ( self.currentMode() != self.Mode.ToolTip ):
            return False
        
        if ( event.type() == event.Leave ):
            pos = object.mapFromGlobal(QCursor.pos())
            if (not object.rect().contains(pos)):
                self.close()
        
        elif ( event.type() in (event.MouseButtonPress, 
                                event.MouseButtonDblClick) ):
            self.close()
        
        return False
    
    def handleButtonClick( self, button ):
        """
        Handles the button click for this widget.  If the Reset button was
        clicked, then the resetRequested signal will be emitted.  All buttons
        will emit the buttonClicked signal.
        
        :param      button | <QAbstractButton>
        """
        if ( self.signalsBlocked() ):
            return
        
        if ( button == self._buttonBox.button(QDialogButtonBox.Reset) ):
            self.resetRequested.emit()
        
        self.buttonClicked.emit(button)
    
    def isResizable( self ):
        """
        Returns if this popup is resizable or not.
        
        :return     <bool>
        """
        return self._resizable
    
    def keyPressEvent( self, event ):
        """
        Looks for the Esc key to close the popup.
        
        :param      event | <QKeyEvent>
        """
        if ( event.key() == Qt.Key_Escape ):
            self.reject()
        
        elif ( event.key() in (Qt.Key_Return, Qt.Key_Enter) ):
            self.accept()
        
        super(XPopupWidget, self).keyPressEvent(event)
    
    def mapAnchorFrom( self, widget, globalPos ):
        """
        Returns the anchor point that best fits within the given widget from
        the inputed global position.
        
        :param      widget      | <QWidget>
                    globalPos   | <QPoint>
        
        :return     <XPopupWidget.Anchor>
        """
        localPos = widget.mapFromGlobal(globalPos)
        
        x = localPos.x()
        y = localPos.y()
        w = widget.width()
        h = widget.height()
        
        cw = self.width() / 2
        ch = self.height() / 2
        
        # by default, try to do a center point, so make sure the center point
        # is at least 1/2 the width longer from each edge
        if ( x < cw and h - y < ch ):
            return XPopupWidget.Anchor.BottomLeft
        elif ( x < cw ):
            return XPopupWidget.Anchor.TopLeft
        elif ( w - x < cw and h - y < ch ):
            return XPopupWidget.Anchor.BottomRight
        elif ( w - x < cw ):
            return XPopupWidget.Anchor.TopRight
        elif ( h - y < ch ):
            return XPopupWidget.Anchor.BottomCenter
        else:
            return XPopupWidget.Anchor.TopCenter
    
    def popup( self, pos = None ):
        """
        Pops up this widget at the inputed position.  The inputed point should \
        be in global space.
        
        :param      pos | <QPoint>
        
        :return     <bool> success
        """
        if ( not self.signalsBlocked() ):
            self.aboutToShow.emit()
        
        if ( not pos ):
            pos = QCursor.pos()
        
        if ( self.currentMode() == XPopupWidget.Mode.Dialog and \
             self.isVisible() ):
            return False
        
        elif ( self.currentMode() == XPopupWidget.Mode.Dialog ):
            self.setPopupMode()
        
        # auto-calculate the point
        if ( self.autoCalculateAnchor() ):
            self.setAnchor(self.mapAnchorFrom( self.parent(), pos ))
        
        pad = self.popupPadding()
        
        # determine where to move based on the anchor
        anchor = self.anchor()
        
        # MODIFY X POSITION
        # align x-left
        if ( anchor & (XPopupWidget.Anchor.TopLeft |
                       XPopupWidget.Anchor.BottomLeft) ):
            pos.setX(pos.x() - pad)
        
        # align x-center
        elif ( anchor & (XPopupWidget.Anchor.TopCenter |
                         XPopupWidget.Anchor.BottomCenter) ):
            pos.setX(pos.x() - self.width() / 2)
        
        # align x-right
        elif ( anchor & (XPopupWidget.Anchor.TopRight |
                         XPopupWidget.Anchor.BottomRight) ):
            pos.setX(pos.x() - self.width() + pad)
        
        # align x-padded
        elif ( anchor & (XPopupWidget.Anchor.RightTop |
                         XPopupWidget.Anchor.RightCenter |
                         XPopupWidget.Anchor.RightBottom) ):
            pos.setX(pos.x() - self.width())
        
        # MODIFY Y POSITION
        # align y-top
        if ( anchor & (XPopupWidget.Anchor.LeftTop |
                       XPopupWidget.Anchor.RightTop) ):
            pos.setY(pos.y() - pad)
        
        # align y-center
        elif ( anchor & (XPopupWidget.Anchor.LeftCenter |
                         XPopupWidget.Anchor.RightCenter) ):
            pos.setY(pos.y() - self.height() / 2)
        
        # align y-bottom
        elif ( anchor & (XPopupWidget.Anchor.LeftBottom |
                         XPopupWidget.Anchor.RightBottom) ):
            pos.setY(pos.y() - self.height() + pad)
        
        # align y-padded
        elif ( anchor & (XPopupWidget.Anchor.BottomLeft |
                         XPopupWidget.Anchor.BottomCenter |
                         XPopupWidget.Anchor.BottomRight) ):
            pos.setY(pos.y() - self.height())
        
        self.adjustMask()
        self.move(pos)
        self.update()
        self.setUpdatesEnabled(True)
        self.show()
        
        if ( self.currentMode() != XPopupWidget.Mode.ToolTip ):
            self.activateWindow()
            
            widget = self.centralWidget()
            if ( widget ):
                self.centralWidget().setFocus()
        
        return True
        
    def paintEvent( self, event ):
        """
        Overloads the paint event to handle painting pointers for the popup \
        mode.
        
        :param      event | <QPaintEvent>
        """
        # use the base technique for the dialog mode
        if ( self.currentMode() == XPopupWidget.Mode.Dialog ):
            super(XPopupWidget, self).paintEvent(event)
            return
        
        # setup the coloring options
        palette = self.palette()
        
        painter = QPainter()
        painter.begin(self)
        
        pen = QPen(palette.color(palette.Window).darker(130))
        pen.setWidthF(1.5)
        painter.setPen(pen)
    
        painter.setRenderHint(painter.Antialiasing)
        painter.setBrush(palette.color(palette.Window))
        painter.drawPath(self.borderPath())
        painter.end()
    
    def popupPadding( self ):
        """
        Returns the amount of pixels to pad the popup arrow for this widget.
        
        :return     <int>
        """
        return self._popupPadding
    
    def reject( self ):
        """
        Emits the accepted signal and closes the popup.
        """
        if ( not self.signalsBlocked() ):
            self.rejected.emit()
        
        if ( self.autoCloseOnReject() ):
            self.close()
        
    def resizeEvent( self, event ):
        """
        Resizes this widget and updates the mask.
        
        :param      event | <QResizeEvent>
        """
        self.setUpdatesEnabled(False)
        super(XPopupWidget, self).resizeEvent(event)
        
        self.adjustMask()
        self.setUpdatesEnabled(True)
        self._sizeGrip.move(self.width() - self._sizeGrip.width(),
                              self.height() - self._sizeGrip.height())
    
    def setAutoCloseOnAccept( self, state ):
        """
        Sets whether or not the popup handles closing for accepting states.
        
        :param      state | <bool>
        """
        self._autoCloseOnAccept = state
    
    def setAutoCloseOnReject( self, state ):
        """
        Sets whether or not the popup handles closing for rejecting states.
        
        :param      state | <bool>
        """
        self._autoCloseOnReject = state
    
    def setCentralWidget( self, widget ):
        """
        Sets the central widget that will be used by this popup.
        
        :param      widget | <QWidget> || None
        """
        self._scrollArea.takeWidget()
        self._scrollArea.setWidget(widget)
        
        self.adjustSize()
    
    def setCurrentMode( self, mode ):
        """
        Sets the current mode for this dialog to the inputed mode.
        
        :param      mode | <XPopupWidget.Mode>
        """
        if ( self._currentMode == mode ):
            return
        
        is_visible = self.isVisible()
        
        self._currentMode = mode
        
        if ( mode == XPopupWidget.Mode.Dialog ):
            self.setWindowFlags(Qt.Dialog | Qt.Tool)
            self._closeButton.setVisible(False)
            self._dialogButton.setVisible(False)
        
        elif ( mode == XPopupWidget.Mode.ToolTip ):
            self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.Tool)
            self.setBackgroundRole(QPalette.Window)
            self.setAttribute(Qt.WA_TransparentForMouseEvents)
            
            policy = Qt.ScrollBarAlwaysOff
            self._closeButton.setVisible(False)
            self._dialogButton.setVisible(False)
            self._buttonBox.setVisible(False)
            
            self._scrollArea.setVerticalScrollBarPolicy(policy)
            self._scrollArea.setHorizontalScrollBarPolicy(policy)
        
        else:
            self.setWindowFlags(Qt.Popup | Qt.Tool | Qt.FramelessWindowHint)
            self._closeButton.setVisible(True)
            self._dialogButton.setVisible(True)
            self.setBackgroundRole(QPalette.Button)
        
        self.adjustContentsMargins()
        
        if ( is_visible ):
            self.show()
    
    def setAnchor( self, anchor ):
        """
        Sets the anchor position for this popup widget to the inputed point.
        
        :param      anchor | <XPopupWidget.Anchor>
        """
        self._anchor = anchor
        self.adjustContentsMargins()
    
    def setAutoCalculateAnchor( self, state ):
        """
        Sets whether or not this widget should auto-calculate the anchor point
        based on the parent position when the popup is triggered.
        
        :param      state | <bool>
        """
        self._autoCalculateAnchor = state
    
    def setDialogMode( self ):
        """
        Sets the current mode value to Dialog.
        """
        self.setCurrentMode(XPopupWidget.Mode.Dialog)
    
    def setToolTipMode( self ):
        """
        Sets the mode for this popup widget to ToolTip
        """
        self.setCurrentMode(XPopupWidget.Mode.ToolTip)
    
    @deprecatedmethod('XPopupWidget',
                      'Direction is no longer used, use setAnchor instead')
    def setDirection( self, direction ):
        """
        Sets the direction for this widget to the inputed direction.
        
        :param      direction | <XPopupWidget.Direction>
        """
        if ( direction == XPopupWidget.Direction.North ):
            self.setAnchor(XPopupWidget.Anchor.TopCenter)
        
        elif ( direction == XPopupWidget.Direction.South ):
            self.setAnchor(XPopupWidget.Anchor.BottomCenter)
        
        elif ( direction == XPopupWidget.Direction.East ):
            self.setAnchor(XPopupWidget.Anchor.LeftCenter)
        
        else:
            self.setAnchor(XPopupWidget.Anchor.RightCenter)
    
    def setPopupMode( self ):
        """
        Sets the current mode value to Popup.
        """
        self.setCurrentMode(XPopupWidget.Mode.Popup)
    
    def setPopupPadding( self, padding ):
        """
        Sets the amount to pad the popup area when displaying this widget.
        
        :param      padding | <int>
        """
        self._popupPadding = padding
        self.adjustContentsMargins()
    
    def setResizable( self, state ):
        self._resizable = state
        self._sizeGrip.setVisible(state)
    
    def setShowTitleBar(self, state):
        self._dialogButton.setVisible(state)
        self._closeButton.setVisible(state)
    
    def setVisible( self, state ):
        super(XPopupWidget, self).setVisible(state)
        widget = self.centralWidget()
        if ( widget ):
            widget.setVisible(state)
    
    def timerEvent( self, event ):
        """
        When the timer finishes, hide the tooltip popup widget.
        
        :param      event | <QEvent>
        """
        self.close()
    
    @staticmethod
    def hideToolTip(key = None):
        """
        Hides any existing tooltip popup widgets.
        """
        try:
            pointer = XPopupWidget._toolTipWidget.pop(key)
        except KeyError:
            return
        
        if ( pointer and pointer() ):
            w = pointer()
            w.setParent(None)
            w.close()
            w.deleteLater()
    
    @staticmethod
    def showToolTip( text,
                     point      = None,
                     anchor     = None,
                     parent     = None,
                     background = None,
                     foreground = None,
                     key        = None,
                     seconds    = 5 ):
        """
        Displays a popup widget as a tooltip bubble.
        
        :param      text        | <str>
                    point       | <QPoint> || None
                    anchor      | <XPopupWidget.Mode.Anchor> || None
                    parent      | <QWidget> || None
                    background  | <QColor> || None
                    foreground  | <QColor> || None
                    key         | <str> || None
                    seconds     | <int>
        """
        if ( point is None ):
            point = QCursor.pos()
        
        if ( parent is None ):
            parent = QApplication.activeWindow()
        
        if ( anchor is None and parent is None ):
            anchor = XPopupWidget.Anchor.TopCenter
        
        # move the existing tip
        pointer = XPopupWidget._toolTipWidget.get(key)
        if ( pointer and pointer() ):
            widget = pointer()
            label  = widget.centralWidget()
            label.setText(text)
            
        else:
            # create a new tooltip widget
            widget = XPopupWidget(parent)
            widget.setToolTipMode()
            widget.setResizable(False)
            widget.setFocusProxy(parent)
            
            parent.installEventFilter(widget)
            
            # create the tooltip label
            label = QLabel(text, widget)
            label.setOpenExternalLinks(True)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            label.setMargin(3)
            label.setIndent(3)
            label.adjustSize()
        
            widget.setCentralWidget(label)
        
        # update the tip
        label.adjustSize()
        widget.adjustSize()
        
        palette = widget.palette()
        if ( not background ):
            background = palette.color(palette.ToolTipBase)
        if ( not foreground ):
            foreground = palette.color(palette.ToolTipText)
        
        palette.setColor(palette.Window,     QColor(background))
        palette.setColor(palette.WindowText, QColor(foreground))
        widget.setPalette(palette)
        widget.centralWidget().setPalette(palette)
        
        if ( anchor is None ):
            widget.setAutoCalculateAnchor(True)
        else:
            widget.setAnchor(anchor)
        
        widget.setAttribute(Qt.WA_DeleteOnClose)
        widget.popup(point)
        widget.startTimer(1000 * seconds)
        
        XPopupWidget._toolTipWidget[key] = weakref.ref(widget)